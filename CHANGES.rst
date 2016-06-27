Changelog
=========

v0.3.0
------

*Unreleased*

- Remove most of the Ansible role dependencies.
  Note that :envvar:`owncloud_autosetup` requires that a webserver is installed to
  initialize the ownCloud database.
  Further configuration will not be possible when the database has not been
  initialized.

  Please run the DebOps playbook to make sure that webserver and database are
  ready. [ypid]

- Wrote initial documentation. [ypid]

- Remove the ``owncloud-server`` package from list of installed packages, it
  has been dropped as of ownCloud 9.0. [drybjed]

- Update :envvar:`owncloud_release` to ``9.0``. [drybjed]

- Installation of the wrapper script for the :command:`occ` command is no
  longer optional as it is needed by the role internally.

  The ``owncloud_enable_occ_shortcut`` variable has no effect anymore and you
  can remove it from your inventory. [ypid]

- Added more LDAP settings. [ypid]

- Reworked ownCloud autosetup tasks. [ypid]

- Refactored :command:`occ` usage in tasks into a separate task file which can be
  included from other parts of the role. This requires Ansible 2.0 to work. [ypid]

- Moved variables defined under :file:`vars/` to :file:`defaults/main.yml` to
  allow to change them. [ypid]

- Fixed :command:`occ` command wrapper to work with ownCloud 8.0. [ypid]

- Switched to `become` for privilege escalation as `recommended by Ansible
  <https://docs.ansible.com/ansible/become.html#for-those-from-pre-1-9-sudo-and-su-still-work>`_.
  [ypid]

- Don’t rely on :file:`/usr/local/bin` being in the `PATH` environment variable
  for this role to work. [ypid]

- Updated Nginx configuration to the example given in the official ownCloud documentation.
  Fixes security warnings which occurred with the latest version of
  ``debops.nginx`` about duplicated security headers. [ypid]

- Use ownCloud APT repository of the latest stable release of ownCloud which is
  supported by this role and not the latest stable release of ownCloud for
  which the DebOps project might need adoption. This allows the role maintainers to
  update the role to new releases, test it and then release a new version of
  the role. [ypid]

- Use :file:`fastcgi_params` instead of :file:`fastcgi.conf` as the FastCGI parameters
  file when ``nginx.org`` flavor is installed, because it is not provided by
  the non-Debian packages. [ypid]

- Support for Debian 7, Ubuntu 12.04 and 14.10 have been dropped due to
  additional work which would be required.
  See https://doc.owncloud.org/server/9.0/admin_manual/installation/linux_installation.html for details.
  If you need support for one of them and can get it to work we will be happy
  about your contribution! [ypid]

- Consolidated ``owncloud_initial_config_*`` and ``owncloud_custom_*conf_map``
  into the ``owncloud_config_*`` namespace. The new variables allow to alter
  settings after the initial setup. [ypid]

- Enabled in memory caching using `APCu <https://pecl.php.net/package/APCu>`_
  by default according to the `official ownCloud Dokumentation
  <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/caching_configuration.html>`_. [ypid]

- Renamed ``owncloud_ldap_enable`` to :envvar:`owncloud__ldap_enabled` to match
  the naming convention of the DebOps project. [ypid]

- Added ownCloud theming support. [ypid]

v0.2.0
------

*Released: 2015-11-12*

- Add Changelog. [ypid]

- Use ``debops.mariadb`` to allow to use MariaDB or MySQL on a remote server. [ypid]

- Updated to ownCloud 8.1. [ypid]

- Allow to use :command:`occ` via Ansible’s inventory. Can be used to enable apps and create users. [ypid]

- Setup shortcut for the :command:`occ` command when not logged in as :envvar:`owncloud_user` user and sudo allows it.
  Disabled by default. Can be enabled via ``owncloud_enable_occ_shortcut``. [ypid]

- Improved LDAP support. Now role will create service account (default: ``cn=owncloud,dc=ansible,dc=fqdn``)
  in LDAP server. You still have to provide proper permission for this account. [scibi]

- New PostgreSQL role support. Now PostgreSQL and MariaDB/MySQL support is unified. [scibi]

- New variable: :envvar:`owncloud_timeout` needed to handle very large files uploads. [scibi]

- Switch ownCloud APT repository to upstream repository, support different Linux
  distributions and releases out of the box. [drybjed]

- Use ``http://`` protocol instead of ``https://`` for APT repository URL,
  because encrypted connection has issues. [drybjed]

- Disabled ``updater`` App as it does not work with this role anyway. [ypid]

v0.1.0
------

*Released: 2015-08-11*

- First release. [drybjed]

