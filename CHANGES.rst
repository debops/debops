Changelog
=========

.. include:: includes/all.rst

**debops.mariadb_server**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.mariadb_server master`_ - unreleased
--------------------------------------------

.. _debops.mariadb_server master: https://github.com/debops/ansible-mariadb_server/compare/v0.2.5...master


`debops.mariadb_server v0.2.5`_ - 2017-09-10
--------------------------------------------

.. _debops.mariadb_server v0.2.5: https://github.com/debops/ansible-mariadb_server/compare/v0.2.4...v0.2.5

Added
~~~~~

- Support MySQL-Galera flavor from Codership. [ganto_]

- Set prerequisite :program:`mysqld` options for database replication when
  using one of the cluster-aware flavors. [ganto_]

- Support set MAX_ALLOWED_PACKET setting for backups. [pedroluislopez_]

Changed
~~~~~~~

- Use the ``inventory_hostname`` instead of the host's FQDN for the Ansible
  ``delegate_to`` option. This ensures that configuration applied by both
  MariaDB roles is idempotent. [drybjed_]

- Fix typo in variable name ``mariadb_server_backup``. [ganto_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

- Generate server and client configuration in different files depending on the
  presence of :file:`/etc/mysql/mariadb.conf.d/` directory. This should fix
  problems with Ansible configuration not applied on MariaDB on newer OS
  releases. [drybjed_]


`debops.mariadb_server v0.2.4`_ - 2016-08-01
--------------------------------------------

.. _debops.mariadb_server v0.2.4: https://github.com/debops/ansible-mariadb_server/compare/v0.2.3...v0.2.4

Changed
~~~~~~~

- The upstream MariaDB repositories use new GPG key to sign the package lists.
  [drybjed_]

- Update documentation and Changelog. [drybjed_]


`debops.mariadb_server v0.2.3`_ - 2016-06-08
--------------------------------------------

.. _debops.mariadb_server v0.2.3: https://github.com/debops/ansible-mariadb_server/compare/v0.2.2...v0.2.3

Changed
~~~~~~~

- Use the ``ini_file`` Ansible module to change the
  :file:`/etc/mysql/debian.cnf` which uses the INI format. [ypid_]

- Don’t fail in Ansible check mode because of undefined variables. [ypid_]


`debops.mariadb_server v0.2.2`_ - 2016-06-02
--------------------------------------------

.. _debops.mariadb_server v0.2.2: https://github.com/debops/ansible-mariadb_server/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Normalize MariaDB configuration templates and variables with accordance to
  suggested format in official MariaDB documentation. [drybjed_]

- Disable ``LOAD DATA LOCAL INFILE`` function for improved security. [drybjed_]


`debops.mariadb_server v0.2.1`_ - 2016-05-29
--------------------------------------------

.. _debops.mariadb_server v0.2.1: https://github.com/debops/ansible-mariadb_server/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Reorganize APT key/repository tasks. Instead of separate tasks for each APT
  key/repository combination use YAML dictionaries to select specific
  repository key and configuration according to selected MariaDB flavor.
  [drybjed_]

- Set ``default-character-set`` option instead of ``character-set-server`` in
  :file:`/etc/mysql/conf.d/client.cnf`. The latter was causing an error when users
  tried to connect to the database using the :command:`mysql` command. [drybjed_]

- Enable use of the default ``domain`` PKI realm, current certificate
  environment managed by debops.pki_ works with the MariaDB/MySQL/Percona
  servers out of the box. [drybjed_]

Removed
~~~~~~~

- Remove all Ansible handlers, the database server is not restarted
  automatically. This should resolve an issue where upstream MariaDB packages
  don't support service reload. [drybjed_]


`debops.mariadb_server v0.2.0`_ - 2016-05-28
--------------------------------------------

.. _debops.mariadb_server v0.2.0: https://github.com/debops/ansible-mariadb_server/compare/v0.1.3...v0.2.0

Added
~~~~~

- Add ``vim`` folding in :file:`defaults/main.yml` and rename task tags. [drybjed_]

Changed
~~~~~~~

- Move configuration of dependent roles and variables from :file:`vars/main.yml` to
  :file:`defaults/main.yml`. The playbooks that uses the ``debops.mariadb_server``
  role needs to be updated to include dependent roles. [drybjed_]

- Rename all ``mariadb_server_`` variables to ``mariadb_server__`` to put the
  role variables in their own namespace. The ``mariadb_server_options_default``
  variable has been renamed to ``mariadb_server__default_options``. [drybjed_]

- Convert :program:`mysqld` and ``client`` Ansible templates to use YAML structures
  for server configuration, split into several default variables. The
  ``mariadb_server__default_options`` variable is renamed to
  :envvar:`mariadb_server__mysqld_performance_options`. [drybjed_]

- Enable the SSL support provided by debops.pki_ only if a corresponding PKI
  realm used by the role is present in the list of known PKI realms. [drybjed_]

- Switch ``vim`` fold markers to new style. [drybjed_]

- Update documentation. [drybjed_]

Migration notes
~~~~~~~~~~~~~~~

When updating from the previous version to this version, you might need to
update your inventory. This oneliner might come in handy to do
this:

.. code:: shell

   git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/mariadb_server__ferm__dependent_rules/mariadb_server__default_options/g;s/\<(mariadb_server)_([^_])/\1__\2/g;'

[ypid_]


`debops.mariadb_server v0.1.3`_ - 2016-05-28
--------------------------------------------

.. _debops.mariadb_server v0.1.3: https://github.com/debops/ansible-mariadb_server/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add default options to the ``debops.mariadb_server`` role via the
  ``mariadb_server_options_default`` variable. [carlalexander]

- Allow to change the backup directory of :program:`automysqlbackup` via
  ``mariadb_server_backup_directory``. [ypid_]

Changed
~~~~~~~

- Fix the :file:`/etc/mysql/conf.d/mysql.cnf` template writing multiple custom
  MariaDB options in one line. [drybjed_]


`debops.mariadb_server v0.1.2`_ - 2015-09-12
--------------------------------------------

.. _debops.mariadb_server v0.1.2: https://github.com/debops/ansible-mariadb_server/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add support for Percona Server as an alternative to MariaDB. [drybjed_]

Changed
~~~~~~~

- Do not delete ``'root'@'localhost'`` database account when hostname is
  ``localhost``. [drybjed_]

- Store the active database flavor in local fact so that other roles can use
  this information if necessary. [drybjed_]


`debops.mariadb_server v0.1.1`_ - 2015-08-21
--------------------------------------------

.. _debops.mariadb_server v0.1.1: https://github.com/debops/ansible-mariadb_server/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add a way to disable :program:`automysqlbackup` support. [drybjed_]


debops.mariadb_server v0.1.0 - 2015-06-18
-----------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
