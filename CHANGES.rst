.. _postgresql_server__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.postgresql_server**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.postgresql_server master`_ - unreleased
-----------------------------------------------

.. _debops.postgresql_server master: https://github.com/debops/ansible-postgresql_server/compare/v0.3.6...master


`debops.postgresql_server v0.3.6`_ - 2017-10-06
-----------------------------------------------

.. _debops.postgresql_server v0.3.6: https://github.com/debops/ansible-postgresql_server/compare/v0.3.5...v0.3.6

Added
~~~~~

- Include custom configuration files from the :file:`conf.d/` directory located
  in the PostgreSQL cluster configuration directory. [drybjed_]

Changed
~~~~~~~

- Rename the ``item.maxworker_processes`` parameter to
  ``item.max_worker_processes`` to use the same name as the configuration
  option. [hvisage, drybjed_]

- Remove the ``sql_inheritance`` option in PostgreSQL 10 configuration files.
  [drybjed_]


`debops.postgresql_server v0.3.5`_ - 2017-09-26
-----------------------------------------------

.. _debops.postgresql_server v0.3.5: https://github.com/debops/ansible-postgresql_server/compare/v0.3.4...v0.3.5

Added
~~~~~

- Allow local connections over IP addresses, in case that PostgreSQL cannot
  correctly resolve the ``localhost`` DNS entry. [drybjed_]


`debops.postgresql_server v0.3.4`_ - 2017-09-15
-----------------------------------------------

.. _debops.postgresql_server v0.3.4: https://github.com/debops/ansible-postgresql_server/compare/v0.3.3...v0.3.4

Changed
~~~~~~~

- Added the :envvar:`postgresql_server__data_directory` variable (defaults to
  the default :file:`/var/lib/postgresql` in Debian) to have a tunable when you
  need/want the default clusters to have a different data_dir base directory.
  This is a server-wide variable and shouldn't be changed once set. [hvisage,
  drybjed_]

- Switched the init service check from custom DebOps core facts to internal
  Ansible facts. This should allow for the role to be used without the
  debops.core_ role. [hvisage, drybjed_]

- The tasks that decide to remove the initial PostgreSQL cluster are more
  specific to make sure that the cluster is not removed accidentally. The
  cluster should not be removed with role Ansible facts are present. [drybjed_]

- Change ``postgresql_server__delegate_to`` to ``inventory_hostname``
  to be in sync with debops.postgresql behavior. [cultcom]

Fixed
~~~~~

- Fix a wrong postgres version check on the main postgresql.conf template. [Erethon]


`debops.postgresql_server v0.3.3`_ - 2016-12-14
-----------------------------------------------

.. _debops.postgresql_server v0.3.3: https://github.com/debops/ansible-postgresql_server/compare/v0.3.2...v0.3.3

Changed
~~~~~~~

- Don't set the ``client_encoding`` option if none is specified in the cluster
  configuration; server will fall back to database encoding for client
  connections. [drybjed_]

- Don't use the ``@`` character in a password to avoid issues with Basic Auth
  URL syntax used for application access. [drybjed_]

- Update the debops.ferm_ configuration in anticipation of the changes in the
  next role release. You might need to remove the existing PostgreSQL firewall
  rule file to avoid duplicating firewall rules. [drybjed_]

Fixed
~~~~~

- Fix the wrong variable name used by the role to decide if the default
  PostgreSQL cluster should be removed on first install. [drybjed_]


`debops.postgresql_server v0.3.2`_ - 2016-10-16
-----------------------------------------------

.. _debops.postgresql_server v0.3.2: https://github.com/debops/ansible-postgresql_server/compare/v0.3.1...v0.3.2

Added
~~~~~

- Add a way to install different PostgreSQL versions after enabling the
  upstream APT repository. [drybjed_]

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]

- Use the debops.core_ Ansible local variables to manage admin account
  configuration. [drybjed_]

- Restrict the characters that can appear in the ``postgres`` user password and
  make the randomly-generated passwords longer. [drybjed_]

Security
~~~~~~~~

- Make sure that the PostgreSQL server stores the admin password encrypted in
  the database. [drybjed_]


`debops.postgresql_server v0.3.1`_ - 2016-06-29
-----------------------------------------------

.. _debops.postgresql_server v0.3.1: https://github.com/debops/ansible-postgresql_server/compare/v0.3.0...v0.3.1

Changed
~~~~~~~

- Expose upstream APT key id and repository URL in default variables. [drybjed_]


`debops.postgresql_server v0.3.0`_ - 2016-06-22
-----------------------------------------------

.. _debops.postgresql_server v0.3.0: https://github.com/debops/ansible-postgresql_server/compare/v0.2.3...v0.3.0

Changed
~~~~~~~

- Rename all role variables from ``postgresql_server_*`` to
  ``postgresql_server__*`` to put them in a separate namespace. You might need
  to update your Ansible inventory. [drybjed_]


`debops.postgresql_server v0.2.3`_ - 2016-04-18
-----------------------------------------------

.. _debops.postgresql_server v0.2.3: https://github.com/debops/ansible-postgresql_server/compare/v0.2.2...v0.2.3

Changed
~~~~~~~

- Change how ``ansible_ssh_user`` variable is detected by the role to fix error
  when it's not set in inventory. [drybjed_]

Fixed
~~~~~

- Fix deprecation warnings on Ansible 2.1.0. [drybjed_]


`debops.postgresql_server v0.2.2`_ - 2016-02-01
-----------------------------------------------

.. _debops.postgresql_server v0.2.2: https://github.com/debops/ansible-postgresql_server/compare/v0.2.1...v0.2.2

Added
~~~~~

- Add configuration variables for debops.apt_preferences_ role, which will
  configure APT on Debian Wheezy to prefer PostgreSQL version from
  ``jessie-backports`` repository (9.4). [drybjed_]

Changed
~~~~~~~

- Change how role detects PostgreSQL version. The new method will use
  ``apt-cache policy`` to use the version determined by APT preferences instead
  of choosing first version from available packages. This fixes an issue when
  multiple PostgreSQL versions are available but the preferred one is not the
  first one. [drybjed_]

- Update the :file:`postgresql.conf` file template to support changes in PostgreSQL
  9.5. [drybjed_]

- Update debops.ferm_ configuration to work with new role templates. The
  :program:`ferm` configuration file is moved to :file:`/etc/ferm/ferm.d/` directory, you
  might want to check the firewall configuration. [drybjed_]

Removed
~~~~~~~

- Remove hard role dependencies on debops.etc_services_ and debops.ferm_
  roles. They will be configured in the service playbook located in
  ``debops-playbooks`` repository. [drybjed_]


`debops.postgresql_server v0.2.1`_ - 2015-11-12
-----------------------------------------------

.. _debops.postgresql_server v0.2.1: https://github.com/debops/ansible-postgresql_server/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Switch from ``sudo_user`` to ``become_user`` parameter. [drybjed_]

- Fix issue with empty ``ansible_ssh_user`` on Ansible v2. [drybjed_]


`debops.postgresql_server v0.2.0`_ - 2015-10-08
-----------------------------------------------

.. _debops.postgresql_server v0.2.0: https://github.com/debops/ansible-postgresql_server/compare/v0.1.0...v0.2.0

Added
~~~~~

- Create list of trusted local PostgreSQL roles.

  Trusted roles can login to PostgreSQL without specifying their password. This
  does not use the ``trust`` authentication method, but a separate list of
  PostgreSQL roles saved in an external file.

  Trusted roles can only login passwordless through the local UNIX socket. This
  means that only UNIX accounts available on the PostgreSQL server can use this
  method. [drybjed_]

- Enable ``trusted`` HBA entry only when list of trusted accounts is not empty
  and not disabled. [drybjed_]

- Add ``postgresql-contrib`` to list of default packages. [drybjed_]

- Install ``pg_top`` by default. [drybjed_]

- Add a variable that enables or disables ``autopostgresqlbackup`` support.
  [drybjed_]

- Add ``postgresql_server_delegate_to`` variable used by Ansible to correctly
  delegate tasks related to role and database management. [drybjed_]

- Add tags to various role tasks. [drybjed_]

Changed
~~~~~~~

- Change how upstream PGDG APT key and repository are managed. Remove the
  unneeded variables and rename ``postgresql_pgdg`` variable to
  ``postgresql_server_upstream``. Move the task from a separate file to the
  main task file. [drybjed_]

- Change what PostgreSQL packages are installed.

  Instead of installing a specific PostgreSQL version directly, install
  ``postgresql`` and ``postgresql-client`` meta-packages. List of packages to
  install is moved to the defaults. [drybjed_]

- Reorganize shared memory configuration. Memory calculations have been moved
  to the default role variables so they are easier to change if needed.
  [drybjed_]

- Get timezone information from host local facts, if available. [drybjed_]

- Check if PostgreSQL can use shared memory through :file:`/dev/shm`. [drybjed_]

- Change how role manages default PostgreSQL version.

  Instead of using a separate static variable, role now checks the version
  installed by the ``postgresql`` meta-package internally and stores that as
  a local Ansible fact to keep the cluster versions stable between upgrades.
  User can install additional PostgreSQL versions as needed using separate list
  of packages to install. [drybjed_]

- Merge separate version-based :file:`postgresql.conf` files into one, which uses
  ``version_compare()`` filter to enable or disable parts of the configuration
  depending on the cluster version. The new configuration file is cleaner,
  without the extra comments that made the previous versions hard to maintain.
  [drybjed_]

- Change the ``postgresql_owner`` and ``postgresql_group`` variabeles to
  ``postgresql_server_user`` and ``postgresql_server_group``. [drybjed_]

- Change the ``postgresql_default_allow`` variable name to
  ``postgresql_server_allow``. [drybjed_]

- Change the ``postgresql_default_postgres_password`` variable to
  ``postgresql_server_admin_password``. [drybjed_]

- Change the ``postgresql_default_log_destination`` variable to
  ``postgresql_server_log_destination``. [drybjed_]

- Change the ``postgresql_default_locale*`` variables to
  ``postgresql_server_locale*``. [drybjed_]

- Redesign of SSL/PKI support using debops.pki_.

  All main PKI-related variables are moved from ``postgresql_pki_*`` namespace
  to ``postgresql_server_pki_*`` namespace. New ``postgresql_server_pki``
  variable specifies if debops.pki_ support and SSL support in general
  should be enabled or disabled in all clusters on a given host. By default
  role checks if debops.pki_ is configured and should automatically disable
  PKI support if it's not.

  Individual clusters can override PKI/SSL settings in their parameters.
  ``item.ssl_*_file`` parameters if specified, now should have absolute paths
  to the respective CA/certificate/private key files. If they are not
  specified, default PKI configuration is used instead. [drybjed_]

- Rename ``postgresql_default_ssl_ciphers`` variable to
  ``postgresql_server_ssl_ciphers``. [drybjed_]

- Rename ``postgresql_default_start_conf`` variable to
  ``postgresql_server_start_conf``.  [drybjed_]

- Rename ``postgresql_sysctl_file`` and ``postgresql_sysctl_values`` variables
  to ``postgresql_server_sysctl_file`` and ``postgresql_server_sysctl_values``.
  [drybjed_]

- Modify how PostgreSQL ``shared_buffers`` are calculated.

  Several variable names have been changed, see commit for details. Role now
  checks if ``kernel.shmmax`` variable has been correctly set and uses that if
  it's lower than the amount of available system RAM. If it's not set
  correctly, role will use amount of available system RAM (about 40% by
  default) as a base for calculations.

  Finished size of ``shared_buffers`` is divided equally between all of the
  PostgreSQL clusters running on a host. [drybjed_]

- Merge the ``postgresql_default_cluster`` and ``postgresql_clusters`` lists
  into ``postgresql_server_clusters`` list. Default cluster configuration has
  been moved to an exposed ``postgresql_server_cluster_main`` dictionary
  included by default in ``postgresql_server_clusters`` list. [drybjed_]

- Switch ``listen_addresses`` PostgreSQL paramter to use YAML list instead of
  string, and expose default list of addresses for all clusters. [drybjed_]

- Rename ``postgresql_default_wal_level`` and
  ``postgresql_default_archive_command`` variables to
  ``postgresql_server_wal_level`` and ``postgresql_server_archive_command``.
  [drybjed_]

- Redesign of the :file:`pg_hba.conf` configuration file.

  Instead of a mix of YAML text blocks and YAML lists,
  ``debops.postgresql_server`` will now use unified dictionary-based HBA
  configuration stored in multiple lists. Configuration file is generated using
  a macro, which allows to use multiple lists at once and filter entries based
  on conditions.

  By default :file:`pg_hba.conf` will contain entries that allow access from local
  networks to which the host is connected directly, requiring SSL to do so. If
  SSL support is disabled, these entries are disabled in the configuration file
  automatically. To allow remote access, you still need to change the list of
  addresses PostgreSQL server listens on and allow access through the firewall.

  Local UNIX accounts have easy access to their own database over PostgreSQL
  UNIX sockets as long as their PostgreSQL role and database names are the same
  as the UNIX account. They can also use all other databases that their role
  has access to automatically. [drybjed_]

- Set ``stats_temp_directory`` location in ``tmpfs``. [drybjed_]

- Redesign of the :file:`pg_ident.conf` configuration file.

  ``postgresql_default_ident`` variable has been removed. Instead, there are
  new variables, ``postgresql_server_ident_system`` and
  ``postgresql_server_ident_local`` which can be used to define ident maps
  (remote ident is not used because it's unreliable as authentication and
  authorization mechanism). Individual clusters can disable the "local" ident
  map and/or specify its own maps using ``item.ident`` parameter.

  Each ident map is specified as a dict with ``item.map`` as name of the map
  (required), ``item.user`` as a list of UNIX user accounts and ``item.role``
  as a list of PostgreSQL roles that create the given map. If list of roles is
  not specified, a mapping for each UNIX account is created with corresponding
  PostgreSQL role. [drybjed_]

- Move the ``pg_hba`` entry that blocks access to ``postgres`` role from remote
  hosts higher up the list. [drybjed_]

- Revoke all public privileges from ``template1`` database. This makes the
  PostgreSQL server more secure by disallowing connections to databases that
  roles don't have explicit access to. [drybjed_]

- Support cluster start and reload on ``systemd`` hosts. [drybjed_]

- Use old ``pg_stat_tmp`` configuration on PostgreSQL 9.1. [drybjed_]

- Replace dots in ``autopostgresqlbackup`` cron script names with underscores,
  so that ``run-parts`` will find and execute them, actually doing the backups
  this time. Ooops... [drybjed_]

- Convert ``autopostgresqlbackup`` configuration from centralized to
  per-cluster. Backup-related variables are renamed from
  ``postgresql_auto_backup_`` to ``postgresql_server_auto_backup_`` namespace
  and normalized to use boolean variables where it's useful. Cron scripts will
  check if PostgreSQL cluster instance is present before performing the backup
  in case that instance was removed. [drybjed_]

- Clean up all Ansible tasks and rewrite them in YAML format. [drybjed_]

- Update the local Ansible facts to use the same format as the client role and
  reload facts in case they have been changed. [drybjed_]

- Allow for public connections to ``template0`` database. This is required by
  some applications like ``phpPgAdmin`` which do not allow selecting the
  database before login. [drybjed_]

- The ``template0`` database does not allow for direct connections from remote
  hosts without additional changes, so instead ``postgres`` database will be
  used to allow "public" connections, with some additional restrictions.
  [drybjed_]

- Move :program:`ferm` firewall rules from a separate template to a default variable
  with configuration that should be passed to debops.ferm_ role. [drybjed_]

- Move debops.etc_services_ configuration from a custom file to the default
  variable which is passed to the role using role dependent variables.
  [drybjed_]

- Update documentation. [drybjed_]

Removed
~~~~~~~

- Remove shared memory configuration from ``debops.postgresql_server``, they
  are now managed by debops.console_ role. [drybjed_]

- Remove :file:`/etc/postgresql-common/user_clusters` configuration from
  ``debops.postgresql_server`` role, it will be configured in the client role.
  [drybjed_]


debops.postgresql_server v0.1.0 - 2015-09-15
--------------------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]
