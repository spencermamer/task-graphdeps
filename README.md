# task-graphdeps
Create a visual chart using [Taskwarrior](https://taskwarrior.org/) and [Graphviz](https://graphviz.org/) utilizing color to indicate task status and arrows to indicate dependency.

## Usage
```python
python graphdeps.py TASKFILTER
```
where `TASKFILTER` is the same as the arguments you would pass to `task` when filtering.

Example:
```python
python graphdeps.py project:fooproject status:pending
```

![Example deps.png file](example.png)

## Installation
Taskwarrior and Graphviz must be installed for the script to work.

### Taskwarrior
[Taskwarrior installation instructions](https://taskwarrior.org/download/)

Ubuntu: `sudo apt-get install taskwarrior`

Fedora: `yum install task`

Arch: `pacman -S task`

### Graphviz
[Graphviz installation instructions](https://www.graphviz.org/download/)

Ubuntu: `apt install graphviz`

Fedora: `yum install graphviz`

Arch: `pacman -S graphviz`

### System-wide usage
To use `graphdeps.py` system-wide on Linux, install or create a link to `/usr/local/bin/` and ensure `/usr/local/bin/` is in your path.
