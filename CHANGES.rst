Changelog
=========

v0.3.0
------

*Unreleased*

- Remove most of the Ansible role dependencies.
  Note that ``owncloud_autosetup`` requires that a webserver is installed to
  initialize the ownCloud database.
  Further configuration will not be possible when the database has not been
  initialized.

  Please run the DebOps playbook to make sure that webserver and database are
  ready. [ypid]

- Wrote initial documentation. [ypid]

- Remove the ``owncloud-server`` package from list of installed packages, it
  has been dropped as of ownCloud 9.0. [drybjed]

- Update ``owncloud_release`` to ``9.0``. [drybjed]

v0.2.0
------

*Released: 2015-11-12*

- Add Changelog. [ypid]

- Use ``debops.mariadb`` to allow to use MariaDB or MySQL on a remote server. [ypid]

- Updated to ownCloud 8.1. [ypid]

- Allow to use ``ooc`` via Ansible’s inventory. Can be used to enable apps and create users. [ypid]

- Setup shortcut for the `occ` command when not logged in as ``owncloud_user`` user and sudo allows it.
  Disabled by default. Can be enabled via ``owncloud_enable_occ_shortcut``. [ypid]

- Improved LDAP support. Now role will create service account (default: ``cn=owncloud,dc=ansible,dc=fqdn``)
  in LDAP server. You still have to provide proper permission for this account. [scibi]

- New PostgreSQL role support. Now PostgreSQL and MariaDB/MySQL support is unified. [scibi]

- New variable: ``owncloud_timeout`` needed to handle very large files uploads. [scibi]

- Switch ownCloud APT repository to upstream repository, support different Linux
  distributions and releases out of the box. [drybjed]

- Use ``http://`` protocol instead of ``https://`` for APT repository URL,
  because encrypted connection has issues. [drybjed]

- Disabled ``updater`` App as it does not work with this role anyway. [ypid]

v0.1.0
------

*Released: 2015-08-11*

- First release. [drybjed]

