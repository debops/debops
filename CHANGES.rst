Changelog
=========

v0.2.2
------

*Released: 2016-06-02*

- Normalize MariaDB configuration templates and variables with accordance to
  suggested format in official MariaDB documentation. [drybjed]

- Disable ``LOAD DATA LOCAL INFILE`` function for improved security. [drybjed]

v0.2.1
------

*Released: 2016-05-29*

- Reorganize APT key/repository tasks. Instead of separate tasks for each APT
  key/repository combination use YAML dictionaries to select specific
  repository key and configuration according to selected MariaDB flavor.
  [drybjed]

- Set ``default-character-set`` option instead of ``character-set-server`` in
  :file:`/etc/mysql/conf.d/client.cnf`. The latter was causing an error when users
  tried to connect to the database using the :command:`mysql` command. [drybjed]

- Enable use of the default ``domain`` PKI realm, current certificate
  environment managed by ``debops.pki`` works with the MariaDB/MySQL/Percona
  servers out of the box. [drybjed]

- Remove all Ansible handlers, the database server is not restarted
  automatically. This should resolve an issue where upstream MariaDB packages
  don't support service reload. [drybjed]

v0.2.0
------

*Released: 2016-05-28*

- Move configuration of dependent roles and variables from :file:`vars/main.yml` to
  :file:`defaults/main.yml`. The playbooks that uses the ``debops.mariadb_server``
  role needs to be updated to include dependent roles. [drybjed]

- Add ``vim`` folding in :file:`defaults/main.yml` and rename task tags. [drybjed]

- Rename all ``mariadb_server_`` variables to ``mariadb_server__`` to put the
  role variables in their own namespace. The ``mariadb_server_options_default``
  variable has been renamed to ``mariadb_server__default_options``. [drybjed]

- Convert ``mysqld`` and ``client`` Ansible templates to use YAML structures
  for server configuration, split into several default variables. [drybjed]

- Enable the SSL support provided by ``debops.pki`` only if a corresponding PKI
  realm used by the role is present in the list of known PKI realms. [drybjed]

- Switch ``vim`` fold markers to new style. [drybjed]

- Update documentation. [drybjed]

Migration notes
^^^^^^^^^^^^^^^

When updating from the previous version to this version, you might need to
update your inventory. This oneliner might come in handy to do
this:

.. code:: shell

   git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/mariadb_server__ferm__dependent_rules/mariadb_server__default_options/g;s/\<(mariadb_server)_([^_])/\1__\2/g;'

[ypid]

v0.1.3
------

*Released: 2016-05-28*

- Add default options to the ``debops.mariadb_server`` role via the
  ``mariadb_server_options_default`` variable. [carlalexander]

- Allow to change the backup directory of :program:`automysqlbackup` via
  ``mariadb_server_backup_directory``. [ypid]

- Fix the :file:`/etc/mysql/conf.d/mysql.cnf` template writing multiple custom
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

- Add a way to disable :program:`automysqlbackup` support. [drybjed]

v0.1.0
------

*Released: 2015-06-18*

- Initial release. [drybjed]

