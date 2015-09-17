Changelog
=========

v0.2.0
------

*Unreleased*

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

v0.1.0
------

*Released: 2015-09-15*

- Add Changelog. [drybjed]

