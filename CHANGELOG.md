## DebOps Changelog


### v0.0.0 (prerelease pending)

***

##### 2014-09-11

* Huge update of the `debops-install` script, which has been renamed to
  `debops-update` and can now both install and update playbooks and roles
  automatically, either in the user home directory at
  `$HOME/.local/share/debops` or in the current directory, or a directory
  specified as a parameter for the script.

##### 2014-09-10

* DebOps project repositories can now be easily backed up using a Bash script

* New main scripts:
  - `debops` - run `ansible-playbook` with custom arguments
  - `debops-task` - run `ansible` with custom arguments

##### 2014-09-07

* First iteration of the `debops-install` script.

* First iteration of the `debops-init` script.

##### 2014-09-01

We are starting the main project repository anew! The old `ginas/ginas`
repository will be preserved for historic reasons as `debops/ginas` after main
project gets up to speed. For now, if you want to play with DebOps, I suggest
heading to [ginas](https://github.com/ginas/ginas/) repository and cloning that
instead. That should be fixed soon though, when new role cloning code takes
shape.


