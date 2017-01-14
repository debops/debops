.. _cryptsetup__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.cryptsetup**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


`debops.cryptsetup master`_ - unreleased
----------------------------------------

.. _debops.cryptsetup master: https://github.com/debops/ansible-owncloud/compare/v0.4.0...master

Added
~~~~~

- Allow to configure the command to shredder/delete the keyfile and header
  backup on remote systems using :envvar:`cryptsetup__keyfile_shred_command`
  and :envvar:`cryptsetup__header_backup_shred_command`. [ypid_]

Changed
~~~~~~~

- Terminate role execution if a vulnerable Ansible version is used to run the
  role as `CVE-2016-8628 <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-8628>`_
  violates one of the design goals of the role.
  The minimum Ansible version without known vulnerabilities is Ansible 2.1.3.
  Refer to `Ansible Security`_ for details. [ypid_]

- Allow to disable management of the filesystem layer for a given device using
  :ref:`item.manage_filesystem <cryptsetup__devices_manage_filesystem>`.
  [ypid_]

- Support to use multiple ciphers and corresponding keys to encrypt one filesystem.
  Refer to :ref:`cryptsetup__ref_devices_chaining_multiple_ciphers` for
  details. [ypid_]

Changed
~~~~~~~

- Require Ansible v2.1 for the role which was needed to implement support for
  chaining multiple cyphers. [ypid_]


`debops.cryptsetup v0.4.0`_ - 2016-10-23
----------------------------------------

.. _debops.cryptsetup v0.4.0: https://github.com/debops/ansible-owncloud/compare/v0.3.1...v0.4.0

Added
~~~~~

- Guides to :ref:`cryptsetup__ref_guide_setup_loop_device` and
  :ref:`cryptsetup__ref_guide_teardown_device`.
  These guides and examples are intended for end users and should help to get
  up and running with the role. [ypid_]

- Allow to overwrite crypto defaults per device. [ypid_]

- Allow to configure the source device where the keyfile will be read from
  using :command:`dd` with :envvar:`cryptsetup__keyfile_source_dev`.
  Intended for integration testing of the role. [ypid_]

Changed
~~~~~~~

- Updated to latest DebOps Standards. [ypid_]

- Changed role namespace from ``cryptsetup_`` to ``cryptsetup__``.
  :regexp:`cryptsetup_[^_]` variables are dropped and don’t have any effect
  anymore.
  Refer to :ref:`cryptsetup__ref_upgrade_nodes_v0.4.0`. [ypid_]

Fixed
~~~~~

- Don’t fail in check mode when the keyfile has not yet been generated.
  This requires to limit the tasks even more which are run in check mode. [ypid_]

- Don’t fail when a device was never in state present and is requested to be
  absent. [ypid_]


`debops.cryptsetup v0.3.1`_ - 2016-04-04
----------------------------------------

.. _debops.cryptsetup v0.3.1: https://github.com/debops/ansible-cryptsetup/compare/v0.3.0...v0.3.1

Changed
~~~~~~~

- No need to have a default for ``cryptsetup_state`` in the tasks.
  ``cryptsetup_state`` is expected to be valid. [ypid_]

Removed
~~~~~~~

- Remove header backups on remote system when ``cryptsetup_header_backup`` is set to ``False``. [ypid_]

Fixed
~~~~~

- Fixed usage of the ``role::cryptsetup:backup`` tag. [ypid_]

- Fixed permission enforcement of the header backup on the Ansible controller. [jacksingleton_]


`debops.cryptsetup v0.3.0`_ - 2016-03-23
----------------------------------------

.. _debops.cryptsetup v0.3.0: https://github.com/debops/ansible-cryptsetup/compare/v0.2.1...v0.3.0

Added
~~~~~

- Added support to setup and mount an encrypted filesystem without storing the
  keyfile on persistent storage of the remote system. [ypid_]

- Added ``cryptsetup_secret_owner``, ``cryptsetup_secret_group`` and
  ``cryptsetup_secret_mode`` to allow to change file permissions of the secrets
  directory and files on the Ansible controller. [ypid_]

Changed
~~~~~~~

- Renamed option ``cryptsetup_backup_header`` to ``cryptsetup_header_backup``
  and fixed the task to allow to disable header backups.
  Fixed: Honor the value of ``item.backup_header`` (``cryptsetup_devices``).
  Only disable header backups when you know what you are doing! [ypid_]

- Renamed option ``cryptsetup_keyfile_location`` to
  ``cryptsetup_secret_path`` as it also contains the header backup on the
  Ansible controller. [ypid_]

- ``cryptsetup_mount_options`` and ``cryptsetup_crypttab_options`` are now
  lists of strings to allow more flexibility. [ypid_]

- Renamed ``cryptsetup_use_random`` to ``cryptsetup_use_dev_random`` to
  emphasize it’s meaning. [ypid_]

Removed
~~~~~~~

- Removed default mount options ``user`` and ``auto`` because they are not good
  defaults for the role. [ypid_]


`debops.cryptsetup v0.2.1`_ - 2015-12-01
----------------------------------------

.. _debops.cryptsetup v0.2.1: https://github.com/debops/ansible-cryptsetup/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Fail when keyfile has been generated but ciphertext block device is not
  available. [ypid_]

- Update :file:`.travis.yml` configuration to test the role on Travis-CI.
  [drybjed_]

- Update documentation and change the required Ansible version to ``v1.9.0``
  due to the ``become`` option replacing :command:`sudo`. [drybjed_]

- Migrated to the DebOps project as ``debops.cryptsetup``. [drybjed_]


`debops.cryptsetup v0.2.0`_ - 2015-10-30
----------------------------------------

.. _debops.cryptsetup v0.2.0: https://github.com/debops/ansible-cryptsetup/compare/v0.1.0...v0.2.0

Added
~~~~~

- Wrote initial documentation. [ypid_]

Changed
~~~~~~~

- Major rewrite to allow to create the crypto and filesystem-layer by this
  role. [ypid_]

- Moved to `DebOps Contrib`_ (the role is still available under
  ``ypid.crypttab`` until it has been fully renamed to something like
  ``debops.cryptsetup``). [ypid_]


debops.cryptsetup v0.1.0 - 2015-09-07
-------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]
