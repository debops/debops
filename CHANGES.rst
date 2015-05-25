Changelog
=========

v0.4.3
------

*Released: 2015-05-25*

- Rearranged documentation. [drybjed]

- Properly propagate exit code when running debops [do3cc]

- Clone and update roles exclusively over HTTPS to allow operation
  over a proxy or in case the git protocol is blocked. [ganto]

v0.4.2
------

*Released: 2015-03-04*

- On OS X search config-file in ``/etc`` too (before searching in
  ``~/Library/Application Support``). [htgoebel]

- Make debops-init write some example values into .debops.cfg.
  [htgoebel]

- Add a work-around for ansible's buggy handling of paths containing
  spaces. [htgoebel]


v0.4.1
------

*Released: 2015-02-26*

- Update role README template to point to new documentation. [drybjed]

- Make Travis mass test script less noisy. [drybjed]

- Add ``library/`` path to default Ansible plugin paths in generated ``ansible.cfg``. [drybjed]

- Define default ``ansible_managed`` variable in generated ``ansible.cfg``. [drybjed]

- Changelog is rewritten in reStructuredText. [drybjed]

v0.4.0
------

*Released: 2015-02-12*

- DebOps can now use a system-wide configuration file `/etc/debops.cfg`. You
  can also install DebOps playbooks and roles in a system-wide location. [htgoebel]

v0.3.0
------

*Released: 2015-01-27*

- Small fixes for bugs in DebOps libraries which prevented corret script
  execution on platforms other than Linux. [htgoebel]

v0.2.0
------

*Released: 2015-01-26*

- ``debops-padlock`` script has been modified to support "lock" and "unlock"
  sub-commands and it is now used by the `padlock` wrapper script to lock and
  unlock EncFS-encrypted secret directory. [htgoebel]

- ``debops`` script can now read configuration from several files::

    /etc/debops.cfg
    $XDG_CONFIG_DIRS/debops.cfg (defaults to ~/etc/xdg/debops.cfg)
    $XDG_CONFIG_HOME/debops.cfg (defaults to ~/.config/debops.cfg)
    ./.debops.cfg

  Configuration options from different files are merged together. [htgoebel]

- Scripts are now tested on Travis-CI using `nosetests`. [drybjed]


v0.1.0
------

*Released: 2014-12-14*

- Scripts are completely rewritten in Python by Hartmut Goebel. This saves
  a lot of code allows for more fertile future changes.

Notable changed related to the shell-version are:

- Playbooks are no longer searched in ``/usr/local/share/debops`` nor in
  ``/usr/share/debops``. We assume DebOps is used from a user account,
  so installing playbooks globally is not the common case.

- Sourcing ``.debops.cfg`` is no longer supported, ``.debops.cfg`` now is
  assumed to be an ini-file.

- The ``ansible_config_hook`` (which was undocumented anyway) is gone.
  Instead you can put sections ``[ansible ...]`` into ``.debops.cfg``
  which will go into ``ansible.cfg``. This allows for easy adding e.g. a
  ``[paramiko]`` section to `ansible.cfg`.

- The padlock-script is no longer used to decide if secrets are
  encrypted. This is now done by testing for the encrypted keyfile and
  the encrypted encfs-config.

- The padlock script still exists and has been simplified a lot. Most
  functionality has been moved into the DebOps python library.

Pre-release
-----------

2014-12-02
~~~~~~~~~~

- `DebOps mailing list`_ has been moved to `groups.io`_.

.. _DebOps mailing list: https://groups.io/org/groupsio/debops
.. _groups.io: https://groups.io/

2014-10-24
~~~~~~~~~~

- all role documentation from their readme files has been moved to `separate
  documentation page`_, role README files will be converted to more
  standardized format, and will use Markdown again, since Ansible Galaxy does
  not support reStructuredText.

.. _separate documentation page: http://docs.debops.org/

- ``debops`` script will automatically generate custom ``ansible.cfg``
  configuration file in project main directory. This file will be used to
  enable custom set of role and plugin paths, which allows for example to
  reorganize playbooks into subdirectories, "overwrite" upstream role with
  local ones via symlinks and enables support for custom Ansible plugins in all
  playbooks and roles.

- DebOps roles will be now cloned in different directory, they are moved from
  ``debops-playbooks/playbooks/roles/`` to ``debops-playbooks/roles/`` (one
  directory up). This allows to overwrite upstream DebOps roles with local
  modified ones, which enables easy development or customization when needed.

- ``debops`` script gains even more integration with DebOps project directory.
  You can put your custom playbooks in ``playbooks/`` or ``ansible/playbooks/``
  directories and access them by specifying name of a playbook as first
  argument of ``debops`` script. Roles can be put in ``roles/`` and
  ``ansible/roles/`` directories and Ansible will automatically look for them
  there. Various plugins can also be put in their respective
  ``ansible/*_plugins/`` directories.

2014-10-21
~~~~~~~~~~

* `DebOps documentation`_ website has been opened to keep documentation in one
  easily searchable place. It's based on `ReadTheDocs`_. All documentation
  already written has been moved from ``debops/debops`` repository to the new
  website, more to come.

.. _DebOps documentation: http://docs.debops.org/
.. _ReadTheDocs: http://readthedocs.org/

2014-09-28
~~~~~~~~~~

- New script has been added, ``debops-defaults``. It can be used to easily work
  with defaults files present in all roles - by default it "aggregates" all of
  them into one stream and sends it to ``view`` command using ``STDOUT``. By
  specifying list of roles on the command line you can select which role
  defaults are aggregated, and by redirecting the script to a file or a command
  you can manipulate it (for example grep for a string).

2014-09-22
~~~~~~~~~~

- ``debops.secret`` main directory has been changed from ``inventory.secret``
  to ``secret`` (the feature that used name of the Ansible inventory as the
  prefix for secret directory has been dropped, because secrets are stored
  inside project directory). Because of that, ``debops*`` scripts are updated
  to support new naming scheme.

- If you use ``debops.secret`` role or DebOps playbooks in general, you will need
  to rename your current plaintext and encrypted directories.

  - ``inventory.secret`` becomes ``secret``

  - ``.encfs.inventory.secret`` becomes ``.encfs.secret``

2014-09-19
~~~~~~~~~~

- All ``debops*`` scripts have been updated with new functions and fixed logic.
  You can now run DebOps commands inside project subdirectories instead of
  just at the root of the project directory.

- ``debops`` script now recognizes encrypted secret directories created by
  ``debops-padlock`` and automatically opens them before Ansible playbook run,
  and closes them afterwards.

- ``debops-init`` will check if you try to create project directory in another
  project and if so, will politely refuse your request.

2014-09-16
~~~~~~~~~~

- New ``debops-padlock`` script, which is a companion Bash script to
  `debops.secret`_ role. It can be used to optionally encrypt secret directory
  using EncFS and GnuPG keys. Main ``debops`` script will be able to recognize
  these encrypted directories and properly open/close them for
  ``ansible-playbook`` runs.

.. _debops.secret: https://github.com/debops/ansible-secret/

2014-09-12
~~~~~~~~~~

- Makefile has been rewritten and streamlined. ``make install`` will install
  all scripts, inventory skeleton and playbooks + roles in a system-wide
  location (by default, ``/usr/local``) and ``make clean`` will remove
  installed files.

- Many different changes in the documentation in preparation of the release.
  Role README files will use new flat-style buttons.

2014-09-11
~~~~~~~~~~

- Huge update of the ``debops-install`` script, which has been renamed to
  ``debops-update`` and can now both install and update playbooks and roles
  automatically, either in the user home directory at
  ``$HOME/.local/share/debops`` or in the current directory, or a directory
  specified as a parameter for the script.

2014-09-10
~~~~~~~~~~

- DebOps project repositories can now be easily backed up using a Bash script

- New main scripts:

  - ``debops`` - run ``ansible-playbook`` with custom arguments

  - ``debops-task`` - run ``ansible`` with custom arguments

2014-09-07
~~~~~~~~~~

- First iteration of the ``debops-install`` script.

- First iteration of the ``debops-init`` script.

2014-09-01
~~~~~~~~~~

We are starting the main project repository anew! The old ``ginas/ginas``
repository will be preserved for historic reasons as ``debops/ginas`` after main
project gets up to speed. For now, if you want to play with DebOps, I suggest
heading to `ginas`_ repository and cloning that
instead. That should be fixed soon though, when new role cloning code takes
shape.

.. _ginas: https://github.com/ginas/ginas/
