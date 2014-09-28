## DebOps Changelog


### v0.1.0 (prerelease pending)

***

##### 2014-09-28

* new script has been added, `debops-defaults`. It can be used to easily work
  with defaults files present in all roles - by default it "aggregates" all
  of them into one stream and sends it to `view` command using STDOUT. By
  specifying list of roles on the command line you can select which role
  defaults are aggregated, and by redirecting the script to a file or
  a command you can manipulate it (for example grep for a string).

##### 2014-09-22

* `debops.secret` main directory has been changed from `inventory.secret` to
  `secret` (the feature that used name of the Ansible inventory as the prefix
  for secret directory has been dropped, because secrets are stored inside
  project directory). Because of that, `debops*` scripts are updated to
  support new naming scheme.

* If you use `debops.secret` role or DebOps playbooks in general, you will need
  to rename your current plaintext and encrypted directories.

  - `inventory.secret` becomes `secret`
  - `.encfs.inventory.secret` becomes `.encfs.secret`

##### 2014-09-19

* All `debops*` scripts have been updated with new functions and fixed logic.
  You can now run DebOps commands inside project subdirectories instead of
  just at the root of the project directory.

* `debops` script now recognizes encrypted secret directories created by
  `debops-padlock` and automatically opens them before Ansible playbook run,
  and closes them afterwards.

* `debops-init` will check if you try to create project directory in another
  project and if so, will politely refuse your request.

##### 2014-09-16

* new `debops-padlock` script, which is a companion Bash script to
  [debops.secret](https://github.com/debops/ansible-secret) role. It can be
  used to optionally encrypt secret directory using EncFS and GnuPG keys. Main
  `debops` script will be able to recognize these encrypted directories and
  properly open/close them for `ansible-playbook` runs.

##### 2014-09-12

* Makefile has been rewritten and streamlined. `make install` will install all
  scripts, inventory skeleton and playbooks + roles in a system-wide location
  (by default, `/usr/local`) and `make clean` will remove installed files.

* many different changes in the documentation in preparation of the release.
  Role README files will use new flat-style buttons.

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


