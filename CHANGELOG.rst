Changelog
=========


This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.


`debops master`_ - unreleased
-----------------------------

.. _debops master: https://github.com/debops/debops/compare/v0.6.0...master

Added
~~~~~

- New Ansible roles have been imported from the ``debops-contrib``
  organization: ``apparmor``, ``bitcoind``, ``btrfs``, ``dropbear_initramfs``,
  ``etckeeper``, ``firejail``, ``foodsoft``, ``fuse``, ``homeassistant``,
  ``kernel_module``, ``kodi``, ``neurodebian``, ``snapshot_snapper``, ``tor``,
  ``volkszaehler``, ``x2go_server``. They are not yet included in the main
  playbook and still need to be renamed to fit with the rest of the
  ``debops.*`` roles.

- New DebOps roles:

  - ``debops.sysfs``: configuration of the Linux kernel attributes through the
    :file:`/sys` filesystem. The role is not enabled by default.

Changed
~~~~~~~

- [debops-tools] The :command:`debops-update` script will now install or
  update the DebOps monorepo instead of separate ``debops-playbooks`` and
  DebOps roles git repositories. Existing installations shouldn't be affected.

- [debops-tools] The :command:`debops` script will now include the DebOps
  monorepo roles and playbooks in the generated :file:`ansible.cfg`
  configuration. The monorepo roles and playbooks are preferred over the old
  ``debops-playbooks`` ones.

  The script is backwards compatible and should work correctly with or without
  the ``debops-playbooks`` repository and roles installed.

- The project repository is tested using :command:`pycodestyle` for compliance
  with Python's `PEP8 Style Guide <https://pep8.org/>`_.

- [debops.nodejs] The ``npm`` package has been removed from Debian Stable.
  The role will now install NPM using the GitHub source, unless upstream NodeJS is
  enabled, which includes its own NPM version.

Removed
~~~~~~~

- [DebOps playbooks] Remove the :file:`ipaddr.py` Ansible filter plugin, it is
  now included in the Ansible core distribution.


debops v0.6.0 - 2017-10-21
--------------------------

Added
~~~~~

- Various repositories that comprise the DebOps project have been merged into
  a single monorepo which will be used as the main development repository.
  Check the :command:`git` log for information about older releases of DebOps
  roles and/or playbooks.
