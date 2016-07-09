.. _owncloud__ref_changelog:

Changelog
=========

**debops.owncloud**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is ypid.

Refer to the :ref:`owncloud__ref_upgrade_nodes` when you intend to upgrade to a
new release.

`debops.owncloud master`_ - unreleased
--------------------------------------

.. _debops.owncloud master: https://github.com/debops/ansible-owncloud/compare/v0.3.0...master

Added
~~~~~

- Wrote initial documentation. [ypid]

- Added more LDAP settings. [ypid]

- Added ownCloud theming support. [ypid]

- Support Redis for file locking. [ypid]

- Install :command:`smbclient` and ImageMagick by default to make
  ownCloud work with SMB shares and thumbnails out of
  the box. [ypid]

- Prepare to use the documents app when setting
  :envvar:`owncloud__app_documents_enabled` to ``True``. [ypid]

- Enabled in memory caching using `APCu <https://pecl.php.net/package/APCu>`_
  by default according to the `official ownCloud Dokumentation
  <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/caching_configuration.html>`_. [ypid]

- Configure fully automated ownCloud security updates by default. [ypid]

Changed
~~~~~~~

- Update :envvar:`owncloud__release` to ``9.0``. [drybjed]

- Installation of the wrapper script for the :command:`occ` command is no
  longer optional as it is needed by the role internally.

  The ``owncloud__enable_occ_shortcut`` variable has no effect anymore and you
  can remove it from your inventory. [ypid]

- Reworked ownCloud autosetup tasks. [ypid]

- Refactored :command:`occ` usage in tasks into a separate task file which can be
  included from other parts of the role. This requires Ansible 2.0 to work. [ypid]

- Moved variables defined under :file:`vars/` to :file:`defaults/main.yml` to
  allow to change them. [ypid]

- Switched to `become` for privilege escalation as `recommended by Ansible
  <https://docs.ansible.com/ansible/become.html#for-those-from-pre-1-9-sudo-and-su-still-work>`_.
  [ypid]

- Use ownCloud APT repository of the latest stable release of ownCloud which is
  supported by this role and not the latest stable release of ownCloud for
  which the DebOps project might need adoption. This allows the role maintainers to
  update the role to new releases, test it and then release a new version of
  the role. [ypid]

- Consolidated ``owncloud__initial_config_*`` and ``owncloud__custom_*conf_map``
  into the ``owncloud__config_*`` namespace. The new variables allow to alter
  settings after the initial setup. [ypid]

- Renamed ``owncloud__ldap_enabledd`` to :envvar:`owncloud__ldap_enabled` to match
  the naming convention of the DebOps project. [ypid]

- Switched the Changelog to `a new format <https://github.com/debops/docs/issues/154>`_. [ypid]

- Renamed Ansible tags ``role::owncloud:mail`` to ``role::owncloud:config``
  and ``role::owncloud:base_install`` to ``role::owncloud:pkg``. [ypid]

Fixed
~~~~~

- Fixed :command:`occ` command wrapper to work with ownCloud 8.0. [ypid]

- Don’t rely on :file:`/usr/local/bin` being in the ``PATH`` environment variable
  for this role to work. [ypid]

- Updated Nginx configuration to the example given in the official ownCloud documentation.
  Fixes security warnings which occurred with the latest version of
  ``debops.nginx`` about duplicated security headers. [ypid]

Removed
~~~~~~~

- Changed role namespace from ``owncloud__`` to ``owncloud__``.
  ``owncloud__[^_]`` variables are dropped and don’t have any effect anymore.
  [ypid]

- Remove most of the Ansible role dependencies.
  Note that :envvar:`owncloud__autosetup` requires that a webserver is installed to
  initialize the ownCloud database.
  Further configuration will not be possible when the database has not been
  initialized.
  This is only important for ownCloud 8.0, for other versions, ``occ`` is used
  to do the auto setup which is more robust.

  Please run the DebOps playbook to make sure that webserver and database are
  ready. [ypid]

- Remove the ``owncloud-server`` package from list of installed packages, it
  has been dropped as of ownCloud 9.0. [drybjed]

- Dropped support for Debian 7, Ubuntu 12.04 and 14.10 due to additional work
  which would be required.
  See https://doc.owncloud.org/server/9.0/admin_manual/installation/linux_installation.html for details.
  If you need support for one of them and can get it to work we will be happy
  about your contribution! [ypid]

`debops.owncloud v0.2.0`_ - 2015-11-12
--------------------------------------

.. _debops.owncloud v0.2.0: https://github.com/debops/ansible-owncloud/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add Changelog. [ypid]

- Allow to use :command:`occ` via Ansible’s inventory. Can be used to enable apps and create users. [ypid]

- Setup shortcut for the :command:`occ` command when not logged in as
  ``owncloud_user`` user and sudo allows it.
  Disabled by default. Can be enabled via ``owncloud_enable_occ_shortcut``.
  [ypid]

- New PostgreSQL role support. Now PostgreSQL and MariaDB/MySQL support is unified. [scibi]

Changed
~~~~~~~

- Use ``debops.mariadb`` to allow to use MariaDB or MySQL on a remote server. [ypid]

- Updated to ownCloud 8.1. [ypid]

- Improved LDAP support. Now role will create service account (default: ``cn=owncloud,dc=ansible,dc=fqdn``)
  in LDAP server. You still have to provide proper permission for this account. [scibi]

- Switch ownCloud APT repository to upstream repository, support different Linux
  distributions and releases out of the box. [drybjed]

- Use ``http://`` protocol instead of ``https://`` for APT repository URL,
  because encrypted connection has issues. [drybjed]

Fixed
~~~~~

- New variable: ``owncloud_timeout`` needed to handle very large files uploads. [scibi]

- Disabled ``updater`` App as it does not work with this role anyway. [ypid]

debops.owncloud v0.1.0 - 2015-08-11
-----------------------------------

Added
~~~~~

- Initial release. [drybjed]
