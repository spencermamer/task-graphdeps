#!/usr/bin/env python
"""Graph dependencies in projects"""
import argparse
import json
from subprocess import Popen, PIPE
import sys
import textwrap


# Typical command line usage:
#
# python graphdeps.py TASKFILTER
#
# TASKFILTER is a taskwarrior filter, documentation can be found here:
# http://taskwarrior.org/projects/taskwarrior/wiki/Feature_filters
#
# Probably the most helpful commands are:
#
# python graphdeps.py project:fooproject status:pending
#  --> graph pending tasks in project 'fooproject'
#
# python graphdeps.py project:fooproject
#  --> graphs all tasks in 'fooproject', pending, completed, deleted
#
# python graphdeps.py status:pending
#  --> graphs all pending tasks in all projects
#
# python graphdeps.py
#  --> graphs everything - could be massive
#

# Wrap label text at this number of characters
CHARS_PER_LINE = 20

# Full list of colors here: http://www.graphviz.org/doc/info/colors.html
COLOR_BLOCKED = 'gold4'
COLOR_MAX_URGENCY = 'red2'  # color of tasks with the highest urgency
COLOR_UNBLOCKED = 'green'
COLOR_DONE = 'grey'
COLOR_WAIT = 'white'
COLOR_DELETED = 'pink'

# The width of the border around the tasks:
BORDER_WIDTH = 1

# Have one HEADER (and only one) uncommented at a time, or the last uncommented
# value will be the only one considered

# Left to right layout, my favorite, ganntt-ish
HEADER = "digraph dependencies { splines=true; overlap=ortho; rankdir=LR; weight=2;"

# Spread tasks on page
# HEADER = "digraph dependencies { layout=neato; splines=true; overlap=scalexy; rankdir=LR; weight=2;"

# More information on setting up graphviz:
# http://www.graphviz.org/doc/info/attrs.html


#-----------------------------------------#
#  Editing under this might break things  #
#-----------------------------------------#

FOOTER = "}"

valid_uuids = list()


def call_taskwarrior(cmd):
    """Call taskwarrior, returning output and error"""
    tw = Popen(['task'] + cmd.split(), stdout=PIPE, stderr=PIPE)
    return tw.communicate()


def get_json(query_parsed):
    """Call taskwarrior, returning objects from json"""
    result, err = call_taskwarrior(
        'export %s rc.json.array=on rc.verbose=nothing' % query_parsed)
    return json.loads(result)


def call_dot(instr):
    """Call dot, returning stdout and stdout"""
    dot = Popen('dot -T png'.split(), stdout=PIPE, stderr=PIPE, stdin=PIPE)
    return dot.communicate(instr)


def main(query, output):
    print('Calling TaskWarrior')
    data = get_json(' '.join(query))

    max_urgency = -9999
    for datum in data:
        if float(datum['urgency']) > max_urgency:
            max_urgency = int(datum['urgency'])

    # first pass: labels
    lines = [HEADER]
    print('Printing labels')
    for datum in data:
        valid_uuids.append(datum['uuid'])
        if datum['description']:

            style = ''
            color = ''
            style = 'filled'

            if datum['status'] == 'pending':
                prefix = str(datum['id']) + '\: '
                if not datum.get('depends', ''):
                    color = COLOR_UNBLOCKED
                else:
                    has_pending_deps = 0
                    for depend in datum['depends'].split(','):
                        for datum2 in data:
                            if datum2['uuid'] == depend and datum2['status'] == 'pending':
                                has_pending_deps = 1
                    if has_pending_deps == 1:
                        color = COLOR_BLOCKED
                    else:
                        color = COLOR_UNBLOCKED

            elif datum['status'] == 'waiting':
                prefix = 'WAIT: '
                color = COLOR_WAIT
            elif datum['status'] == 'completed':
                prefix = 'DONE: '
                color = COLOR_DONE
            elif datum['status'] == 'deleted':
                prefix = 'DELETED: '
                color = COLOR_DELETED
            else:
                prefix = ''
                color = 'white'

            if float(datum['urgency']) == max_urgency:
                color = COLOR_MAX_URGENCY

            label = ''
            description_lines = textwrap.wrap(
                datum['description'], CHARS_PER_LINE)
            for desc_line in description_lines:
                label += desc_line + "\\n"

            lines.append('"%s"[shape=box][BORDER_WIDTH=%d][label="%s%s"][fillcolor=%s][style=%s]' % (
                datum['uuid'], BORDER_WIDTH, prefix, label, color, style))
            # documentation http://www.graphviz.org/doc/info/attrs.html

    # second pass: dependencies
    print('Resolving dependencies')
    for datum in data:
        if datum['description']:
            for dep in datum.get('depends', '').split(','):
                if dep != '' and dep in valid_uuids:
                    lines.append('"%s" -> "%s";' % (dep, datum['uuid']))
                    continue

    lines.append(FOOTER)

    print('Calling dot')
    png, err = call_dot('\n'.join(lines).encode('utf-8'))
    if err not in ('', b''):
        print('Error calling dot:')
        print(err.strip())

    print('Writing to ' + output)
    with open(output, 'wb') as f:
        f.write(png)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create dependency trees')
    parser.add_argument('query', nargs='+',
                       help='Taskwarrior query')
    parser.add_argument('-o', '--output', default='deps.png',
                       help='output filename')

    args = parser.parse_args()
    main(args.query, args.output)
