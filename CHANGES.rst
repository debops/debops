Changelog
=========

v0.1.2
------

*Unreleased*

- Do not delete ``'root'@'localhost'`` database account when hostname is
  ``localhost``. [drybjed]

- Add support for Percona Server as an alternative to MariaDB. [drybjed]

- Store the active database flavor in local fact so that other roles can use
  this information if necessary. [drybjed]

v0.1.1
------

*Released: 2015-08-21*

- Add a way to disable ``automysqlbackup`` support. [drybjed]

v0.1.0
------

*Released: 2015-06-18*

- Initial release. [drybjed]

