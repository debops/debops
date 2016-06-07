Changelog
=========

v0.3.0
------

*Unreleased*

- Remove most of the Ansible role dependencies.
  Note that :any:`owncloud_autosetup` requires that a webserver is installed to
  initialize the ownCloud database.
  Further configuration will not be possible when the database has not been
  initialized.

  Please run the DebOps playbook to make sure that webserver and database are
  ready. [ypid]

- Wrote initial documentation. [ypid]

- Remove the ``owncloud-server`` package from list of installed packages, it
  has been dropped as of ownCloud 9.0. [drybjed]

- Update :any:`owncloud_release` to ``9.0``. [drybjed]

- Installation of the wrapper script for the :command:`occ` command is no
  longer optional as it is needed by the role internally.

  The ``owncloud_enable_occ_shortcut`` variable has no effect anymore and you
  can remove it from your inventory. [ypid]

- Added more LDAP settings. [ypid]

- Reworked ownCloud autosetup tasks. [ypid]

- Refactored ``occ`` usage in tasks into a separate task file which can be
  included from other parts of the role. This requires Ansible 2.0 to work. [ypid]

- Moved variables defined under :file:`vars/` to :file:`defaults/main.yml` to
  allow to change them. [ypid]

- Fixed ``occ`` command wrapper to work with ownCloud 8.0. [ypid]

- Switched to `become` for privilege escalation as `recommended by Ansible
  <https://docs.ansible.com/ansible/become.html#for-those-from-pre-1-9-sudo-and-su-still-work>`_.
  [ypid]

v0.2.0
------

*Released: 2015-11-12*

- Add Changelog. [ypid]

- Use ``debops.mariadb`` to allow to use MariaDB or MySQL on a remote server. [ypid]

- Updated to ownCloud 8.1. [ypid]

- Allow to use ``occ`` via Ansible’s inventory. Can be used to enable apps and create users. [ypid]

- Setup shortcut for the ``occ`` command when not logged in as :any:`owncloud_user` user and sudo allows it.
  Disabled by default. Can be enabled via ``owncloud_enable_occ_shortcut``. [ypid]

- Improved LDAP support. Now role will create service account (default: ``cn=owncloud,dc=ansible,dc=fqdn``)
  in LDAP server. You still have to provide proper permission for this account. [scibi]

- New PostgreSQL role support. Now PostgreSQL and MariaDB/MySQL support is unified. [scibi]

- New variable: :any:`owncloud_timeout` needed to handle very large files uploads. [scibi]

- Switch ownCloud APT repository to upstream repository, support different Linux
  distributions and releases out of the box. [drybjed]

- Use ``http://`` protocol instead of ``https://`` for APT repository URL,
  because encrypted connection has issues. [drybjed]

- Disabled ``updater`` App as it does not work with this role anyway. [ypid]

v0.1.0
------

*Released: 2015-08-11*

- First release. [drybjed]

