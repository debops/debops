.. _mariadb__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.mariadb**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.

Refer to the :ref:`mariadb__ref_upgrade_notes` when you intend to upgrade to a
new release.


`debops.mariadb master`_ - unreleased
-------------------------------------

.. _debops.mariadb master: https://github.com/debops/ansible-mariadb/compare/v0.2.2...master

Added
~~~~~

- Support MySQL-Galera flavor from Codership. [ganto_]

- Support to specify ``encoding`` and ``collation`` for
  :envvar:`mariadb__databases`. [ypid_]

Changed
~~~~~~~

- Use ``inventory_hostname`` as fallback for task delegation which should render
  manual definition of :envvar:`mariadb__delegate_to` unnecessary in case the client
  and server are setup on the same host and the inventory name doesn't
  correspond with the FQDN of the host. [ganto_]

- Generate client configuration in different files depending on the presence of
  :file:`/etc/mysql/mariadb.conf.d/` directory. This should fix problems with
  Ansible configuration not applied on MariaDB on newer OS releases. [drybjed_]


`debops.mariadb v0.2.2`_ - 2016-08-01
-------------------------------------

.. _debops.mariadb v0.2.2: https://github.com/debops/ansible-mariadb/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- The upstream MariaDB repositories use new GPG key to sign the package lists.
  [drybjed_]

- Update documentation and Changelog. [drybjed_]


`debops.mariadb v0.2.1`_ - 2016-06-02
-------------------------------------

.. _debops.mariadb v0.2.1: https://github.com/debops/ansible-mariadb/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Normalize configuration templates and variables in accordance with official
  MariaDB documentation. [drybjed_]


`debops.mariadb v0.2.0`_ - 2016-05-29
-------------------------------------

.. _debops.mariadb v0.2.0: https://github.com/debops/ansible-mariadb/compare/v0.1.2...v0.2.0

Added
~~~~~

- Add support for client-side SSL configuration, enabled when the database is
  located on a different host. The SSL support is enabled automatically when
  debops.pki_ environment is configured. [drybjed_]

- Add custom variables for users and databases defined by other Ansible roles
  via dependent variables. Also, ensure that old legacy lists of databases and
  users are still supported. [drybjed_]

Changed
~~~~~~~

- Fixed Ansible check mode. [ypid_]

- Move variables from :file:`vars/main.yml` to :file:`defaults/main.yml`. Add ``vim``
  fold markers in :file:`defaults/main.yml`. [drybjed_]

- Rename all role variables to put them in their own namespace. [drybjed_]

- Move MariaDB client configuration from template into YAML structures.
  [drybjed_]

- Update documentation. [drybjed_]

- Redesign the APT key/repository Ansible tasks to use YAML dictionaries with
  data based on selected database flavor. [drybjed_]


`debops.mariadb v0.1.2`_ - 2016-05-28
-------------------------------------

.. _debops.mariadb v0.1.2: https://github.com/debops/ansible-mariadb/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Changed tag from ``mariadb/contents`` to ``role::mariadb:contents`` to
  control database contents tasks. [ypid_]

- Allow to change the file path for the credentials file which defaults to
  ``~/.my.cnf``. [ypid_]


`debops.mariadb v0.1.1`_ - 2015-09-12
-------------------------------------

.. _debops.mariadb v0.1.1: https://github.com/debops/ansible-mariadb/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add support for Percona Server client as an alternative to MariaDB. [drybjed_]

Changed
~~~~~~~

- Change the order of tasks in the role so that database and user creation can
  use Ansible local facts immediately. [drybjed_]

- Store the active database flavor as a fact so other roles can use it if
  necessary. [drybjed_]


debops.mariadb v0.1.0 - 2015-06-23
----------------------------------

Added
~~~~~

- Initial release. [drybjed_]
