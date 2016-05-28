Changelog
=========

v0.1.3
------

*Unreleased*

- Fixed Ansible check mode. [ypid]

v0.1.2
------

*Released: 2016-05-28*

- Changed tag from ``mariadb/contents`` to ``role::mariadb:contents`` to
  control database contents tasks. [ypid]

- Allow to change the file path for the credentials file which defaults to
  ``~/.my.cnf``. [ypid]


v0.1.1
------

*Released: 2015-09-12*

- Change the order of tasks in the role so that database and user creation can
  use Ansible local facts immediately. [drybjed]

- Add support for Percona Server client as an alternative to MariaDB. [drybjed]

- Store the active database flavor as a fact so other roles can use it if
  necessary. [drybjed]

v0.1.0
------

*Released: 2015-06-23*

- Initial release. [drybjed]

