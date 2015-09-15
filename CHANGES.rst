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

v0.1.0
------

*Released: 2015-09-15*

- Add Changelog. [drybjed]

