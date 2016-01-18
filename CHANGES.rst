Changelog
=========

v0.3.0
------

*Unreleased*

- Renamed option ``cryptsetup_backup_header`` to ``cryptsetup_header_backup``
  and fixed the task to allow to disable header backups.
  Only disable header backups when you know what you are doing! [ypid]

- Added support to setup and mount a encrypted filesystem without storing the
  keyfile on persistent storage of the remote system. [ypid]

- Removed default mount options ``user`` and ``auto`` because they are not good
  defaults for the role. [ypid]

v0.2.1
------

*Released: 2015-12-01*

- Fail when keyfile has been generated but ciphertext block device is not
  available. [ypid]

- Update :file:`.travis.yml` configuration to test the role on Travis-CI.
  [drybjed]

- Update documentation and change the required Ansible version to ``v1.9.0``
  due to the ``become`` option replacing ``sudo``. [drybjed]

- Migrated to the DebOps project as ``debops.cryptsetup``. [drybjed]

v0.2.0
------

*Released: 2015-10-30*

- Major rewrite to allow to create the crypto and filesystem-layer by this
  role. [ypid]

- Wrote initial documentation. [ypid]

- Moved to `DebOps Contrib`_ (the role is still available under
  `ypid.crypttab`_ until it has been fully renamed to something like
  ``debops.cryptsetup``). [ypid]

v0.1.0
------

*Released: 2015-09-07*

- Initial release. [ypid]

.. _ypid.crypttab: https://galaxy.ansible.com/detail#/role/4559
.. _DebOps Contrib: https://github.com/debops-contrib/
