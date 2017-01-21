Changelog
=========

**debops.mariadb_server**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.mariadb_server master`_ - unreleased
--------------------------------------------

.. _debops.mariadb_server master: https://github.com/debops/ansible-mariadb_server/compare/v0.2.4...master

Added
~~~~~

- Support MySQL-Galera flavor from Codership. [ganto]

- Set prerequisite :program:`mysqld` options for database replication when
  using one of the cluster-aware flavors. [ganto]

Changed
~~~~~~~

- Use the ``inventory_hostname`` instead of the host's FQDN for the Ansible
  ``delegate_to`` option. This ensures that configuration applied by both
  MariaDB roles is idempotent. [drybjed]

- Fix typo in variable name ``mariadb_server_backup``. [ganto]


`debops.mariadb_server v0.2.4`_ - 2016-08-01
--------------------------------------------

.. _debops.mariadb_server v0.2.4: https://github.com/debops/ansible-mariadb_server/compare/v0.2.3...v0.2.4

Changed
~~~~~~~

- The upstream MariaDB repositories use new GPG key to sign the package lists.
  [drybjed]

- Update documentation and Changelog. [drybjed]


`debops.mariadb_server v0.2.3`_ - 2016-06-08
--------------------------------------------

.. _debops.mariadb_server v0.2.3: https://github.com/debops/ansible-mariadb_server/compare/v0.2.2...v0.2.3

Changed
~~~~~~~

- Use the ``ini_file`` Ansible module to change the
  :file:`/etc/mysql/debian.cnf` which uses the INI format. [ypid]

- Don’t fail in Ansible check mode because of undefined variables. [ypid]


`debops.mariadb_server v0.2.2`_ - 2016-06-02
--------------------------------------------

.. _debops.mariadb_server v0.2.2: https://github.com/debops/ansible-mariadb_server/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Normalize MariaDB configuration templates and variables with accordance to
  suggested format in official MariaDB documentation. [drybjed]

- Disable ``LOAD DATA LOCAL INFILE`` function for improved security. [drybjed]


`debops.mariadb_server v0.2.1`_ - 2016-05-29
--------------------------------------------

.. _debops.mariadb_server v0.2.1: https://github.com/debops/ansible-mariadb_server/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

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

Removed
~~~~~~~

- Remove all Ansible handlers, the database server is not restarted
  automatically. This should resolve an issue where upstream MariaDB packages
  don't support service reload. [drybjed]


`debops.mariadb_server v0.2.0`_ - 2016-05-28
--------------------------------------------

.. _debops.mariadb_server v0.2.0: https://github.com/debops/ansible-mariadb_server/compare/v0.1.3...v0.2.0

Added
~~~~~

- Add ``vim`` folding in :file:`defaults/main.yml` and rename task tags. [drybjed]

Changed
~~~~~~~

- Move configuration of dependent roles and variables from :file:`vars/main.yml` to
  :file:`defaults/main.yml`. The playbooks that uses the ``debops.mariadb_server``
  role needs to be updated to include dependent roles. [drybjed]

- Rename all ``mariadb_server_`` variables to ``mariadb_server__`` to put the
  role variables in their own namespace. The ``mariadb_server_options_default``
  variable has been renamed to ``mariadb_server__default_options``. [drybjed]

- Convert ``mysqld`` and ``client`` Ansible templates to use YAML structures
  for server configuration, split into several default variables. The
  ``mariadb_server__default_options`` variable is renamed to
  ``mariadb_server__mysqld_performance_options``. [drybjed]

- Enable the SSL support provided by ``debops.pki`` only if a corresponding PKI
  realm used by the role is present in the list of known PKI realms. [drybjed]

- Switch ``vim`` fold markers to new style. [drybjed]

- Update documentation. [drybjed]

Migration notes
~~~~~~~~~~~~~~~

When updating from the previous version to this version, you might need to
update your inventory. This oneliner might come in handy to do
this:

.. code:: shell

   git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/mariadb_server__ferm__dependent_rules/mariadb_server__default_options/g;s/\<(mariadb_server)_([^_])/\1__\2/g;'

[ypid]


`debops.mariadb_server v0.1.3`_ - 2016-05-28
--------------------------------------------

.. _debops.mariadb_server v0.1.3: https://github.com/debops/ansible-mariadb_server/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add default options to the ``debops.mariadb_server`` role via the
  ``mariadb_server_options_default`` variable. [carlalexander]

- Allow to change the backup directory of :program:`automysqlbackup` via
  ``mariadb_server_backup_directory``. [ypid]

Changed
~~~~~~~

- Fix the :file:`/etc/mysql/conf.d/mysql.cnf` template writing multiple custom
  MariaDB options in one line. [drybjed]


`debops.mariadb_server v0.1.2`_ - 2015-09-12
--------------------------------------------

.. _debops.mariadb_server v0.1.2: https://github.com/debops/ansible-mariadb_server/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add support for Percona Server as an alternative to MariaDB. [drybjed]

Changed
~~~~~~~

- Do not delete ``'root'@'localhost'`` database account when hostname is
  ``localhost``. [drybjed]

- Store the active database flavor in local fact so that other roles can use
  this information if necessary. [drybjed]


`debops.mariadb_server v0.1.1`_ - 2015-08-21
--------------------------------------------

.. _debops.mariadb_server v0.1.1: https://github.com/debops/ansible-mariadb_server/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add a way to disable :program:`automysqlbackup` support. [drybjed]


debops.mariadb_server v0.1.0 - 2015-06-18
-----------------------------------------

Added
~~~~~

- Initial release. [drybjed]
