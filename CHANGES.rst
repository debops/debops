Changelog
=========

**debops.mariadb**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.mariadb master`_ - unreleased
-------------------------------------

.. _debops.mariadb master: https://github.com/debops/ansible-mariadb/compare/v0.2.2...master


`debops.mariadb v0.2.2`_ - 2016-08-01
-------------------------------------

.. _debops.mariadb v0.2.2: https://github.com/debops/ansible-mariadb/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- The upstream MariaDB repositories use new GPG key to sign the package lists.
  [drybjed]

- Update documentation and Changelog. [drybjed]


`debops.mariadb v0.2.1`_ - 2016-06-02
-------------------------------------

.. _debops.mariadb v0.2.1: https://github.com/debops/ansible-mariadb/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Normalize configuration templates and variables in accordance with official
  MariaDB documentation. [drybjed]


`debops.mariadb v0.2.0`_ - 2016-05-29
-------------------------------------

.. _debops.mariadb v0.2.0: https://github.com/debops/ansible-mariadb/compare/v0.1.2...v0.2.0

Added
~~~~~

- Add support for client-side SSL configuration, enabled when the database is
  located on a different host. The SSL support is enabled automatically when
  ``debops.pki`` environment is configured. [drybjed]

- Add custom variables for users and databases defined by other Ansible roles
  via dependent variables. Also, ensure that old legacy lists of databases and
  users are still supported. [drybjed]

Changed
~~~~~~~

- Fixed Ansible check mode. [ypid]

- Move variables from ``vars/main.yml`` to ``defaults/main.yml``. Add ``vim``
  fold markers in ``defaults/main.yml``. [drybjed]

- Rename all role variables to put them in their own namespace. [drybjed]

- Move MariaDB client configuration from template into YAML structures.
  [drybjed]

- Update documentation. [drybjed]

- Redesign the APT key/repository Ansible tasks to use YAML dictionaries with
  data based on selected database flavor. [drybjed]


`debops.mariadb v0.1.2`_ - 2016-05-28
-------------------------------------

.. _debops.mariadb v0.1.2: https://github.com/debops/ansible-mariadb/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Changed tag from ``mariadb/contents`` to ``role::mariadb:contents`` to
  control database contents tasks. [ypid]

- Allow to change the file path for the credentials file which defaults to
  ``~/.my.cnf``. [ypid]


`debops.mariadb v0.1.1`_ - 2015-09-12
-------------------------------------

.. _debops.mariadb v0.1.1: https://github.com/debops/ansible-mariadb/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add support for Percona Server client as an alternative to MariaDB. [drybjed]

Changed
~~~~~~~

- Change the order of tasks in the role so that database and user creation can
  use Ansible local facts immediately. [drybjed]

- Store the active database flavor as a fact so other roles can use it if
  necessary. [drybjed]


debops.mariadb v0.1.0 - 2015-06-23
----------------------------------

Added
~~~~~

- Initial release. [drybjed]
