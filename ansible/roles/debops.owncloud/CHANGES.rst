.. _owncloud__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.owncloud**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is ypid_.

Refer to the :ref:`owncloud__ref_upgrade_nodes` when you intend to upgrade to a
new release.


`debops.owncloud master`_ - unreleased
--------------------------------------

.. _debops.owncloud master: https://github.com/debops/ansible-owncloud/compare/v0.3.0...master

Added
~~~~~

- Add support for the `Apache HTTP Server`_, founded by https://www.hamcos.de/. [ypid_]

- Add Ansible tags for env roles. To only prepare the ownCloud role
  environment, you can use the ``role::owncloud:env`` tag. [ypid_]

- Provide various configuration options from the :file:`config.php` file using
  Ansible facts. Refer to :ref:`owncloud__ref_ansible_facts` for details. [ypid_]

- Allow to leave third party apps enabled during/after upgrades via
  :envvar:`owncloud__auto_database_upgrade_3party_app_disable`.
  Defaults to upstream default. [ypid_]

- Add experimental NextCloud 11 support, tested on Debian Stretch. [ypid_]

Changed
~~~~~~~

- Renamed variables to be consistent with DebOps:

  * ``owncloud__nginx__servers`` → :envvar:`owncloud__nginx__dependent_servers`
  * ``owncloud__nginx__upstream_php`` → :envvar:`owncloud__nginx__dependent_upstreams`

  The role bundles a script which can do this transition for you.
  Refer to :ref:`owncloud__ref_upgrade_nodes_v0.4.0` for details.

- Allow use of multiple FQDN addresses in :envvar:`owncloud__fqdn` as a YAML
  list. [drybjed_]

- Update the ``ldap_entry`` task to use new ``attributes`` parameter with the
  new Ansible module version. The new module is `planned to be merged in Ansible <https://github.com/ansible/ansible-modules-extras/pull/2952>`_
  and has already been updated in the `debops-playbooks repository <https://github.com/debops/debops-playbooks>`_
  for feature parity with Ansible version in the future. [drybjed_]

- Fix typo in variable name by renaming ``owncloud__theme_entity_name`` to
  :envvar:`owncloud__theme_entity_name`. [jbicha]

- Derive LDAP port from :envvar:`owncloud__ldap_port`. [ypid_]

- Offload ``logrotate`` rule management to the debops.logrotate_ role. [ypid_]

Removed
~~~~~~~

- Removed deprecated Ansible inventory group ``debops_owncloud``. Refer to the
  :ref:`owncloud__ref_getting_started` guide. [ypid_]

- Drop support for ownCloud 8.2 and below. 8.2 is End of Life as of 8.2.11 (2017-04-18). [ypid_]

Fixed
~~~~~

- Ansible 2.2 support for usage in integration testing.
  Version 2.2 mentions a few deprecation warnings.
  We are aware of this but there is not much we can do yet as Ansible 2.1
  support should be retained for this release. [ypid_]

- Fix :envvar:`owncloud__webserver` and ``owncloud.webserver`` Ansible fact
  generation. ``groups`` is not a list of the groups of the current host but a
  dictionary of all groups. Use ``group_names``. [ypid_]

- Don’t attempt to run certain :command:`occ` subcommands when ownCloud is in
  maintenance mode as some subcommands are not available in maintenance mode.
  This kind of restricts the use of the maintenance mode for this role when you
  want to use those :command:`occ` subcommands.
  As a result, this role does not enable or disable maintenance mode and
  the role maintainers recommend to leave maintainers mode disabled. [ypid_]

- Fix playbook to handle the ``role::nginx`` Ansible tag correctly. [ypid_]

- Fix custom directory creating. Previously, the Ansible role did not ensure
  that custom directories the administrator might had configured using
  :envvar:`owncloud__data_path` and :envvar:`owncloud__nginx_client_body_temp_path`
  actually existed and failed when reloading the respective services. [ypid_]

Security
~~~~~~~~

- Update to the new ``ownCloud build service`` OpenPGP key with fingerprint
  ``DDA2 C105 C4B7 3A66 49AD  2BBD 47AE 7F72 479B C94B``.

  Note that new releases are signed with that key. If the new key is not
  present, no updates will be installed because they can not be verified.
  Thus updates fixing potential security issues will not be installed!

  Please run the updated role with the new key against your host(s) to fix
  this. [ypid_]

- Switch back to importing the OpenPGP key from a key file shipped with
  this role to mitigate a vulnerability in the `Ansible apt_key module`_.

  Refer to `apt_key module does not verify key fingerprints <https://github.com/ansible/ansible-modules-core/issues/5237>`_
  for details. [ypid_]

- Ensure that old or unused OpenPGP public keys which where previously used to
  sign the APT repository are absent.
  This is done to mitigate the possibility of one of the keys getting
  compromised. [ypid_]

- Require at least Ansible 2.1.4 to run the role. Refer to `Ansible Security`_ for details.
  Note that the requirement is currently not enforced by Ansible so you could
  run the role with older Ansible versions but you really should not! [ypid_]


`debops.owncloud v0.3.0`_ - 2016-09-17
--------------------------------------

.. _debops.owncloud v0.3.0: https://github.com/debops/ansible-owncloud/compare/v0.2.0...v0.3.0

Added
~~~~~

- Wrote documentation. [ypid_]

- More LDAP settings. [ypid_]

- ownCloud theming support. [ypid_]

- Support Redis for file locking. [ypid_]

- Install ImageMagick by default to make ownCloud work thumbnails out of the
  box. [ypid_]

- Added :envvar:`owncloud__smb_support` for easy enabling of SMB support
  (disabled by default). [ypid_]

- Prepare to use the documents app when setting
  :envvar:`owncloud__app_documents_enabled` to ``True``. [ypid_]

- Enabled in memory caching using `APCu <https://pecl.php.net/package/APCu>`_
  by default according to the `official ownCloud documentation
  <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/caching_configuration.html>`_. [ypid_]

- Support fully automated ownCloud security updates (disabled by default). [ypid_]

- Support to configure ownCloud applications. [ypid_]

- :envvar:`owncloud__dependent_packages`,
  :envvar:`owncloud__dependent_occ_cmd_list` and
  :envvar:`owncloud__dependent_apps_config` in a idempotence safe way even when
  this role is run standalone without having the variables set.
  This allows other roles to use functionality provided by this role. [ypid_]

- :envvar:`owncloud__apt_preferences__dependent_list_optional` variable which
  might come in handy when APT preference presets are used. [ypid_]

- :envvar:`owncloud__temp_path` to allow to change the temp directory of
  ownCloud. [ypid_]

- :envvar:`owncloud__user_files` and similar lists to allow to allow you to
  manage files for ownCloud users. [ypid_]

- :ref:`owncloud__ref_external_users` documentation. [ypid_]

- :ref:`owncloud__ref_external_storage` documentation. [ypid_]

- :envvar:`owncloud_ldap_update_settings` which allows to that the
  settings from :envvar:`owncloud__ldap_conf_map` are up-to-date on the remote
  system. [ypid_]

- Tested ownCloud ``9.1`` support. Setup works fine but this release of the
  role will mainly support ownCloud ``9.0``. [ypid_]

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
  which DebOps might need adoption. This allows the role maintainers to
  update the role to new releases, test it and then release a new version of
  the role. [ypid_]

- Consolidated ``owncloud__initial_config_*`` and ``owncloud__custom_*conf_map``
  into the ``owncloud__config_*`` namespace. The new variables allow to alter
  settings after the initial setup. [ypid_]

- Switched the Changelog to `a new format <https://github.com/debops/docs/issues/154>`_. [ypid_]

- Introduced :envvar:`owncloud_ldap_update_settings` set to ``True``.
  Previously, this was not configurable and the LDAP settings where not updated in
  ownCloud after LDAP was configured. [ypid_]

- Switched from the ``debops.php5`` role to the new and unified debops.php_
  role and tested PHP7.0 support. [ypid_]

- Support large file uploads by increasing the :envvar:`owncloud__timeout`
  from ``300`` to ``3600`` and the :envvar:`owncloud__upload_size` from
  ``128M`` to ``2G``. [ypid_]

- Support to run the :command:`occ` wrapper script as :envvar:`owncloud__app_user`
  which can be useful for scripting. [ypid_]

- Changed default ownCloud domain from ``owncloud.{{ ansible_domain }}`` to
  ``cloud.{{ ansible_domain }}`` to generalize the role.
  Note that this migration might leave some legacy files on the remote host in place.
  Test this before or overwrite this change using :envvar:`owncloud__domain`.
  [ypid_]

- Renamed Ansible tags

  * ``role::owncloud:base_install`` → ``role::owncloud:pkg``
  * ``role::owncloud:mail`` → ``role::owncloud:config``

  [ypid_]

- Renamed variables to be consistent with DebOps:

  * :regexp:`owncloud__?run_occ_global_commands` → :envvar:`owncloud__occ_cmd_list`
  * :regexp:`owncloud__?run_occ_group_commands` → :envvar:`owncloud__group_occ_cmd_list`
  * :regexp:`owncloud__?run_occ_host_commands` → :envvar:`owncloud__host_occ_cmd_list`
  * :regexp:`owncloud__?packages_optional` → Removed, refer to :envvar:`owncloud__smb_support`
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
  * :regexp:`owncloud__?enable_apc_cli` → Removed, refer to :envvar:`owncloud__apcu_enabled`

  The role bundles a script which can do this transition for you.
  Refer to :ref:`owncloud__ref_upgrade_nodes_v0.3.0` for details.

  [ypid_]

- Use the debops.core_ local facts as a base for the :envvar:`owncloud__domain`
  variable instead of using the ``ansible_domain`` variable directly.
  [drybjed_]

- Rename the ``owncloud__subdomain`` variable to :envvar:`owncloud__fqdn`, and
  use it to set the FQDN of the ownCloud service. [drybjed_]

- The :envvar:`owncloud__fqdn` variable is used as the mail domain, the mail
  "from" account is changed from ``owncloud__subdomain`` variable to
  ``noreply`` string. [drybjed_]

- Use a static filename of the :program:`nginx` server configuration file. This might
  require manual removal of the old :program:`nginx` server configuration file on
  existing installations. [drybjed_]

- Support to use a Redis password as configured by debops.redis_
  v0.2.0 automatically. [ypid_]

Deprecated
~~~~~~~~~~

- Deprecated ownCloud 8.0 support which is End of Life as of 8.0.15 (2016-09-20). [ypid_]

Removed
~~~~~~~

- Changed role namespace from ``owncloud_`` to ``owncloud__``.
  :regexp:`owncloud_[^_]` variables are dropped and don’t have any effect
  anymore. [ypid_]

- Remove most of the Ansible role dependencies.

  Please run the DebOps playbook to make sure that webserver and database are
  ready. [ypid_]

- Remove the ``owncloud-server`` package from list of installed packages, it
  has been dropped as of ownCloud 9.0. [drybjed_]

- Dropped support for Debian 7, Ubuntu 12.04 and 14.10 due to additional work
  which would be required.
  See https://doc.owncloud.org/server/9.0/admin_manual/installation/linux_installation.html for details.
  If you need support for one of them and can get it to work we will be happy
  about your contribution! [ypid_]

- Drop ownCloud 7.0 support which is End of Life as of 7.0.15 (2016-05-12). [ypid_]

Fixed
~~~~~

- Fixed :command:`occ` command wrapper to work with ownCloud 8.0. [ypid_]

- Don’t rely on :file:`/usr/local/bin` being in the ``PATH`` environment variable
  for this role to work. [ypid_]

- Updated Nginx configuration to the example given in the official ownCloud documentation.
  Fixes security warnings which occurred with the latest version of
  debops.nginx_ about duplicated security headers. [ypid_]

- Fix error when strings handed over to :command:`occ maintenance:install` start with a hyphen.
  This only affected the initial setup and the role would have failed previously.
  If the role worked for you, then you where not affected by this bug
  (occurrence of this bug was random based on the generated passwords). [ypid_]


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

- Updated to ownCloud ``8.1``. [ypid_]

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
