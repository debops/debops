.. _owncloud__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.owncloud**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer_ is ypid_.

Refer to the :ref:`owncloud__ref_upgrade_nodes` when you intend to upgrade to a
new release.

`debops.owncloud master`_ - unreleased
--------------------------------------

.. _debops.owncloud master: https://github.com/debops/ansible-owncloud/compare/v0.2.0...master

Added
~~~~~

- Wrote initial documentation. [ypid_]

- Added more LDAP settings. [ypid_]

- Added ownCloud theming support. [ypid_]

- Support Redis for file locking. [ypid_]

- Install :command:`smbclient` and ImageMagick by default to make
  ownCloud work with SMB shares and thumbnails out of
  the box. [ypid_]

- Prepare to use the documents app when setting
  :envvar:`owncloud__app_documents_enabled` to ``True``. [ypid_]

- Enabled in memory caching using `APCu <https://pecl.php.net/package/APCu>`_
  by default according to the `official ownCloud Dokumentation
  <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/caching_configuration.html>`_. [ypid_]

- Configure fully automated ownCloud security updates by default. [ypid_]

- Support to configure ownCloud applications. [ypid_]

- Added :envvar:`owncloud__dependent_packages`,
  :envvar:`owncloud__dependent_occ_cmd_list` and
  :envvar:`owncloud__dependent_apps_config` in a idempotence safe way even when
  this role is run standalone without having the variables set.
  This allows other roles to use functionality provided by this role. [ypid_]

- Added :envvar:`owncloud__apt_preferences__dependent_list_optional` variable
  which might come in handy when APT preference presets are used. [ypid_]

- Added :envvar:`owncloud__temp_path` to allow to change the temp directory of
  ownCloud. [ypid_]

- Added :envvar:`owncloud__user_files` and similar lists to allow to allow you
  to manage files for ownCloud users. [ypid_]

- Added :ref:`owncloud__ref_external_users` documentation. [ypid_]

- Added :envvar:`owncloud_ldap_update_settings` which allows to that the
  settings from :envvar:`owncloud__ldap_conf_map` are up-to-date on the remote
  system. [ypid_]

Changed
~~~~~~~

- Update :envvar:`owncloud__release` to ``9.0``. [drybjed_]

- Installation of the wrapper script for the :command:`occ` command is no
  longer optional as it is needed by the role internally.

  The ``owncloud__enable_occ_shortcut`` variable has no effect anymore and you
  can remove it from your inventory. [ypid_]

- Reworked ownCloud autosetup tasks. [ypid_]

- Refactored :command:`occ` usage in tasks into a separate task file which can be
  included from other parts of the role. This requires Ansible 2.0 to work. [ypid_]

- Moved variables defined under :file:`vars/` to :file:`defaults/main.yml` to
  allow to change them. [ypid_]

- Switched to `become` for privilege escalation as `recommended by Ansible
  <https://docs.ansible.com/ansible/become.html#for-those-from-pre-1-9-sudo-and-su-still-work>`_.
  [ypid_]

- Use ownCloud APT repository of the latest stable release of ownCloud which is
  supported by this role and not the latest stable release of ownCloud for
  which the DebOps project might need adoption. This allows the role maintainers to
  update the role to new releases, test it and then release a new version of
  the role. [ypid_]

- Consolidated ``owncloud__initial_config_*`` and ``owncloud__custom_*conf_map``
  into the ``owncloud__config_*`` namespace. The new variables allow to alter
  settings after the initial setup. [ypid_]

- Switched the Changelog to `a new format <https://github.com/debops/docs/issues/154>`_. [ypid_]

- Introduced :envvar:`owncloud_ldap_update_settings` set to ``True``.
  Previously, this was not configurable and the LDAP settings where not updated in
  ownCloud after LDAP was configured. [ypid_]

- Switched from the debops.php5 role to the new and unified debops.php_ role. [ypid_]

- Renamed Ansible tags

  * ``role::owncloud:base_install`` → ``role::owncloud:pkg``
  * ``role::owncloud:mail`` → ``role::owncloud:config``

  [ypid_]

- Renamed variables to be consistent with the DebOps project:

  * :regexp:`owncloud__?run_occ_global_commands` → :envvar:`owncloud__occ_cmd_list`
  * :regexp:`owncloud__?run_occ_group_commands` → :envvar:`owncloud__group_occ_cmd_list`
  * :regexp:`owncloud__?run_occ_host_commands` → :envvar:`owncloud__host_occ_cmd_list`
  * :regexp:`owncloud__?packages_optional` → :envvar:`owncloud__optional_packages`
  * :regexp:`owncloud__?packages_group` → :envvar:`owncloud__group_packages`
  * :regexp:`owncloud__?packages_host` → :envvar:`owncloud__host_packages`
  * :regexp:`owncloud__?config_group` → :envvar:`owncloud__group_config`
  * :regexp:`owncloud__?config_host` → :envvar:`owncloud__host_config`
  * :regexp:`owncloud__?apps_config_group` → :envvar:`owncloud__group_apps_config`
  * :regexp:`owncloud__?apps_config_host` → :envvar:`owncloud__host_apps_config`
  * :regexp:`owncloud__?config_role_required` → :envvar:`owncloud__role_config`
  * :regexp:`owncloud__?config_role_optional` → :envvar:`owncloud__role_recommended_config`
  * :regexp:`owncloud__?ldap_enable` → :envvar:`owncloud__ldap_enabled`
  * :regexp:`owncloud__?php5_max_children` → :envvar:`owncloud__php_max_children`
  * :regexp:`owncloud__?php5_output_buffering` → :envvar:`owncloud__php_output_buffering`
  * :regexp:`owncloud__?php5__pool` → :envvar:`owncloud__php__dependent_pools`

  [ypid_]

Removed
~~~~~~~

- Changed role namespace from ``owncloud_`` to ``owncloud__``.
  :regexp:`owncloud_[^_]` variables are dropped and don’t have any effect
  anymore. [ypid_]

- Remove most of the Ansible role dependencies.
  Note that :envvar:`owncloud__autosetup` requires that a webserver is installed to
  initialize the ownCloud database.
  Further configuration will not be possible when the database has not been
  initialized.
  This is only important for ownCloud 8.0, for other versions, :command:`occ` is used
  to do the auto setup which is more robust.

  Please run the DebOps playbook to make sure that webserver and database are
  ready. [ypid_]

- Remove the ``owncloud-server`` package from list of installed packages, it
  has been dropped as of ownCloud 9.0. [drybjed_]

- Dropped support for Debian 7, Ubuntu 12.04 and 14.10 due to additional work
  which would be required.
  See https://doc.owncloud.org/server/9.0/admin_manual/installation/linux_installation.html for details.
  If you need support for one of them and can get it to work we will be happy
  about your contribution! [ypid_]

Fixed
~~~~~

- Fixed :command:`occ` command wrapper to work with ownCloud 8.0. [ypid_]

- Don’t rely on :file:`/usr/local/bin` being in the ``PATH`` environment variable
  for this role to work. [ypid_]

- Updated Nginx configuration to the example given in the official ownCloud documentation.
  Fixes security warnings which occurred with the latest version of
  debops.nginx_ about duplicated security headers. [ypid_]


`debops.owncloud v0.2.0`_ - 2015-11-12
--------------------------------------

.. _debops.owncloud v0.2.0: https://github.com/debops/ansible-owncloud/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add Changelog. [ypid_]

- Allow to use :command:`occ` via Ansible’s inventory. Can be used to enable apps and create users. [ypid_]

- Setup shortcut for the :command:`occ` command when not logged in as
  ``owncloud_user`` user and sudo allows it.
  Disabled by default. Can be enabled via ``owncloud_enable_occ_shortcut``.
  [ypid_]

- New PostgreSQL role support. Now PostgreSQL and MariaDB/MySQL support is unified. [scibi_]

Changed
~~~~~~~

- Use debops.mariadb_ to allow to use MariaDB or MySQL on a remote server. [ypid_]

- Updated to ownCloud 8.1. [ypid_]

- Improved LDAP support. Now role will create service account (default: ``cn=owncloud,dc=ansible,dc=fqdn``)
  in LDAP server. You still have to provide proper permission for this account. [scibi_]

- Switch ownCloud APT repository to upstream repository, support different Linux
  distributions and releases out of the box. [drybjed_]

- Use ``http://`` protocol instead of ``https://`` for APT repository URL,
  because encrypted connection has issues. [drybjed_]

Fixed
~~~~~

- New variable: ``owncloud_timeout`` needed to handle very large files uploads. [scibi_]

- Disabled ``updater`` App as it does not work with this role anyway. [ypid_]

debops.owncloud v0.1.0 - 2015-08-11
-----------------------------------

Added
~~~~~

- Initial release. [drybjed_]
