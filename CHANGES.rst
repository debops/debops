Changelog
=========

v0.2.0
------

*Unreleased*

- Move configuration of dependent roles and variables from ``vars/main.yml`` to
  ``defaults/main.yml``. The playbooks that use ``debops.mariadb_server`` role
  need to be updated to include dependent roles. [drybjed]

- Add ``vim`` folding in ``defaults/main.yml`` and rename task tags. [drybjed]

- Rename all ``mariadb_server_`` variables to ``mariadb_server__`` to put the
  role variables in their own namespace. The ``mariadb_server_options_default``
  variable has been renamed to ``mariadb_server__default_options``. [drybjed]

- Convert ``mysqld`` and ``client`` Ansible templates to use YAML structures
  for server configuration, split into several default variables. [drybjed]

v0.1.3
------

*Released: 2016-05-28*

- Add default options to the ``debops.mariadb_server`` role via the
  ``mariadb_server_options_default`` variable. [carlalexander]

- Allow to change the backup directory of ``automysqlbackup`` via
  ``mariadb_server_backup_directory``. [ypid]

- Fix the ``/etc/mysql/conf.d/mysql.cnf`` template writing multiple custom
  MariaDB options in one line. [drybjed]

v0.1.2
------

*Released: 2015-09-12*

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

