Changelog
=========

v0.2.1
------

*Released: 2016-06-02*

- Normalize configuration templates and variables in accordance with official
  MariaDB documentation. [drybjed]

v0.2.0
------

*Released: 2016-05-29*

- Fixed Ansible check mode. [ypid]

- Move variables from ``vars/main.yml`` to ``defaults/main.yml``. Add ``vim``
  fold markers in ``defaults/main.yml``. [drybjed]

- Rename all role variables to put them in their own namespace. [drybjed]

- Move MariaDB client configuration from template into YAML structures.
  [drybjed]

- Add support for client-side SSL configuration, enabled when the database is
  located on a different host. The SSL support is enabled automatically when
  ``debops.pki`` environment is configured. [drybjed]

- Add custom variables for users and databases defined by other Ansible roles
  via dependent variables. Also, ensure that old legacy lists of databases and
  users are still supported. [drybjed]

- Update documentation. [drybjed]

- Redesign the APT key/repository Ansible tasks to use YAML dictionaries with
  data based on selected database flavor. [drybjed]

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

