Changelog
=========

v0.2.2
------

*Unreleased*

- Change how role detects PostgreSQL version. The new method will use
  ``apt-cache policy`` to use the version determined by APT preferences instead
  of choosing first version from available packages. This fixes an issue when
  multiple PostgreSQL versions are available but the preferred one is not the
  first one. [drybjed]

- Update the ``postgresql.conf`` file template to support changes in PostgreSQL
  9.5. [drybjed]

v0.2.1
------

*Released: 2015-11-12*

- Switch from ``sudo_user`` to ``become_user`` parameter. [drybjed]

- Fix issue with empty ``ansible_ssh_user`` on Ansible v2. [drybjed]

v0.2.0
------

*Released: 2015-10-08*

- Change how upstream PGDG APT key and repository are managed. Remove the
  unneeded variables and rename ``postgresql_pgdg`` variable to
  ``postgresql_server_upstream``. Move the task from a separate file to the
  main task file. [drybjed]

- Change what PostgreSQL packages are installed.

  Instead of installing a specific PostgreSQL version directly, install
  ``postgresql`` and ``postgresql-client`` meta-packages. List of packages to
  install is moved to the defaults. [drybjed]

- Reorganize shared memory configuration. Memory calculations have been moved
  to the default role variables so they are easier to change if needed.
  [drybjed]

- Get timezone information from host local facts, if available. [drybjed]

- Check if PostgreSQL can use shared memory through ``/dev/shm``. [drybjed]

- Change how role manages default PostgreSQL version.

  Instead of using a separate static variable, role now checks the version
  installed by the ``postgresql`` meta-package internally and stores that as
  a local Ansible fact to keep the cluster versions stable between upgrades.
  User can install additional PostgreSQL versions as needed using separate list
  of packages to install. [drybjed]

- Merge separate version-based ``postgresql.conf`` files into one, which uses
  ``version_compare()`` filter to enable or disable parts of the configuration
  depending on the cluster version. The new configuration file is cleaner,
  without the extra comments that made the previous versions hard to maintain.
  [drybjed]

- Change the ``postgresql_owner`` and ``postgresql_group`` variabeles to
  ``postgresql_server_user`` and ``postgresql_server_group``. [drybjed]

- Change the ``postgresql_default_allow`` variable name to
  ``postgresql_server_allow``. [drybjed]

- Change the ``postgresql_default_postgres_password`` variable to
  ``postgresql_server_admin_password``. [drybjed]

- Change the ``postgresql_default_log_destination`` variable to
  ``postgresql_server_log_destination``. [drybjed]

- Change the ``postgresql_default_locale*`` variables to
  ``postgresql_server_locale*``. [drybjed]

- Redesign of SSL/PKI support using ``debops.pki``.

  All main PKI-related variables are moved from ``postgresql_pki_*`` namespace
  to ``postgresql_server_pki_*`` namespace. New ``postgresql_server_pki``
  variable specifies if ``debops.pki`` support and SSL support in general
  should be enabled or disabled in all clusters on a given host. By default
  role checks if ``debops.pki`` is configured and should automatically disable
  PKI support if it's not.

  Individual clusters can override PKI/SSL settings in their parameters.
  ``item.ssl_*_file`` parameters if specified, now should have absolute paths
  to the respective CA/certificate/private key files. If they are not
  specified, default PKI configuration is used instead. [drybjed]

- Rename ``postgresql_default_ssl_ciphers`` variable to
  ``postgresql_server_ssl_ciphers``. [drybjed]

- Rename ``postgresql_default_start_conf`` variable to
  ``postgresql_server_start_conf``.  [drybjed]

- Rename ``postgresql_sysctl_file`` and ``postgresql_sysctl_values`` variables
  to ``postgresql_server_sysctl_file`` and ``postgresql_server_sysctl_values``.
  [drybjed]

- Remove shared memory configuration from ``debops.postgresql_server``, they
  are now managed by ``debops.console`` role. [drybjed]

- Modify how PostgreSQL ``shared_buffers`` are calculated.

  Several variable names have been changed, see commit for details. Role now
  checks if ``kernel.shmmax`` variable has been correctly set and uses that if
  it's lower than the amount of available system RAM. If it's not set
  correctly, role will use amount of available system RAM (about 40% by
  default) as a base for calculations.

  Finished size of ``shared_buffers`` is divided equally between all of the
  PostgreSQL clusters running on a host. [drybjed]

- Merge the ``postgresql_default_cluster`` and ``postgresql_clusters`` lists
  into ``postgresql_server_clusters`` list. Default cluster configuration has
  been moved to an exposed ``postgresql_server_cluster_main`` dictionary
  included by default in ``postgresql_server_clusters`` list. [drybjed]

- Switch ``listen_addresses`` PostgreSQL paramter to use YAML list instead of
  string, and expose default list of addresses for all clusters. [drybjed]

- Rename ``postgresql_default_wal_level`` and
  ``postgresql_default_archive_command`` variables to
  ``postgresql_server_wal_level`` and ``postgresql_server_archive_command``.
  [drybjed]

- Redesign of the ``pg_hba.conf`` configuration file.

  Instead of a mix of YAML text blocks and YAML lists,
  ``debops.postgresql_server`` will now use unified dictionary-based HBA
  configuration stored in multiple lists. Configuration file is generated using
  a macro, which allows to use multiple lists at once and filter entries based
  on conditions.

  By default ``pg_hba.conf`` will contain entries that allow access from local
  networks to which the host is connected directly, requiring SSL to do so. If
  SSL support is disabled, these entries are disabled in the configuration file
  automatically. To allow remote access, you still need to change the list of
  addresses PostgreSQL server listens on and allow access through the firewall.

  Local UNIX accounts have easy access to their own database over PostgreSQL
  UNIX sockets as long as their PostgreSQL role and database names are the same
  as the UNIX account. They can also use all other databases that their role
  has access to automatically. [drybjed]

- Set ``stats_temp_directory`` location in ``tmpfs``. [drybjed]

- Remove ``/etc/postgresql-common/user_clusters`` configuration from
  ``debops.postgresql_server`` role, it will be configured in the client role.
  [drybjed]

- Redesign of the ``pg_ident.conf`` configuration file.

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
  PostgreSQL role. [drybjed]

- Create list of trusted local PostgreSQL roles.

  Trusted roles can login to PostgreSQL without specifying their password. This
  does not use the ``trust`` authentication method, but a separate list of
  PostgreSQL roles saved in an external file.

  Trusted roles can only login passwordless through the local UNIX socket. This
  means that only UNIX accounts available on the PostgreSQL server can use this
  method. [drybjed]

- Add ``postgresql-contrib`` to list of default packages. [drybjed]

- Move the ``pg_hba`` entry that blocks access to ``postgres`` role from remote
  hosts higher up the list. [drybjed]

- Install ``pg_top`` by default. [drybjed]

- Revoke all public privileges from ``template1`` database. This makes the
  PostgreSQL server more secure by disallowing connections to databases that
  roles don't have explicit access to. [drybjed]

- Support cluster start and reload on ``systemd`` hosts. [drybjed]

- Enable ``trusted`` HBA entry only when list of trusted accounts is not empty
  and not disabled. [drybjed]

- Use old ``pg_stat_tmp`` configuration on PostgreSQL 9.1. [drybjed]

- Replace dots in ``autopostgresqlbackup`` cron script names with underscores,
  so that ``run-parts`` will find and execute them, actually doing the backups
  this time. Ooops... [drybjed]

- Convert ``autopostgresqlbackup`` configuration from centralized to
  per-cluster. Backup-related variables are renamed from
  ``postgresql_auto_backup_`` to ``postgresql_server_auto_backup_`` namespace
  and normalized to use boolean variables where it's useful. Cron scripts will
  check if PostgreSQL cluster instance is present before performing the backup
  in case that instance was removed. [drybjed]

- Add a variable that enables or disables ``autopostgresqlbackup`` support.
  [drybjed]

- Clean up all Ansible tasks and rewrite them in YAML format. [drybjed]

- Add ``postgresql_server_delegate_to`` variable used by Ansible to correctly
  delegate tasks related to role and database management. [drybjed]

- Update the local Ansible facts to use the same format as the client role and
  reload facts in case they have been changed. [drybjed]

- Allow for public connections to ``template0`` database. This is required by
  some applications like ``phpPgAdmin`` which do not allow selecting the
  database before login. [drybjed]

- The ``template0`` database does not allow for direct connections from remote
  hosts without additional changes, so instead ``postgres`` database will be
  used to allow "public" connections, with some additional restrictions.
  [drybjed]

- Move ``ferm`` firewall rules from a separate template to a default variable
  with configuration that should be passed to ``debops.ferm`` role. [drybjed]

- Move ``debops.etc_services`` configuration from a custom file to the default
  variable which is passed to the role using role dependent variables.
  [drybjed]

- Add tags to various role tasks. [drybjed]

- Update documentation. [drybjed]

v0.1.0
------

*Released: 2015-09-15*

- Add Changelog. [drybjed]

