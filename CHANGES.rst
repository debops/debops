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

v0.1.0
------

*Released: 2015-09-15*

- Add Changelog. [drybjed]

