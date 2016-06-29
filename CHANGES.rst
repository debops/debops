Changelog
=========

v0.3.1
------

*Released: 2016-06-29*

- Expose upstream APT key fingerprint and repository URL in default variables.
  [drybjed]

- Don't log role tasks that might deal with PostgreSQL passwords. [drybjed]

v0.3.0
------

*Released: 2016-06-23*

- Rename all role variables from ``postgresql_*`` to ``postgresql__*`` to move
  them to a separate namespace. You might need to update your inventory.
  [drybjed]

- Add new ``postgresql__dependent_*`` variables for use by other roles.
  [drybjed]

- Add support for database extension management. [drybjed]

v0.2.1
------

*Released: 2016-02-01*

- Change how role detects PostgreSQL version. The new method will use
  ``apt-cache policy`` to use the version determined by APT preferences instead
  of choosing first version from available packages. This fixes an issue when
  multiple PostgreSQL versions are available but the preferred one is not the
  first one. [drybjed]

- Add configuration variables for ``debops.apt_preferences`` role. The
  configuration will make sure that PostgreSQL 9.4 from ``jessie-backports``
  repository is installed on Debian Wheezy hosts. [drybjed]

v0.2.0
------

*Released: 2015-10-13*

- Remove parts of the role that are related to PostgreSQL server management. [drybjed]

- Add support for upstream PostgreSQL repository. [drybjed]

- Clean up package installation code. [drybjed]

- Add client-side management of PostgreSQL roles and databases. [drybjed]

- Add an option to set role password expiration. [drybjed]

- Update documentation. [drybjed]

v0.1.0
------

*Released: 2015-09-25*

- Add Changelog. [drybjed]

