Changelog
=========

.. include:: includes/all.rst

**debops-contrib.roundcube**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ganto_.


`debops-contrib.roundcube master`_ - unreleased
-----------------------------------------------

.. _debops-contrib.roundcube master: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.3...master


`debops-contrib.roundcube v0.1.3_` - 2017-07-26
-----------------------------------------------

.. _debops-contrib.roundcube v0.1.3: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Set default version to 1.1.9. [ganto_]


Fixed
~~~~~

- Fix documentation build error due to deleted link definition to deprecated
  `debops.php5` role repository. [ganto_]
- Probe if :envvar:`roundcube__domain` is a string and construct :envvar:`roundcube__git_checkout` accordingly.  [cultcom]


`debops-contrib.roundcube v0.1.2_` - 2017-03-09
-----------------------------------------------

.. _debops-contrib.roundcube v0.1.2: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Set default version to 1.1.7. [ganto_]

- Moved all variable definitions to :file:`defaults/main.yml` for better
  configurability. Restructured defaults configuration file. [ganto_]

Fixed
~~~~~

- Properly pass ``password`` parameter to debops.mariadb_ role dependency. [cultcom]

- Fix ``login_host`` definition in database schema import. [cultcom]

- Fix syntax error in :envvar:`roundcube__database_schema` variable definition. [cultcom]

- Fix MySQL database schema setup when using remote database by adjusting
  indentation of example playbook. [ganto_]


`debops-contrib.roundcube v0.1.1_` - 2016-08-03
-----------------------------------------------

.. _debops-contrib.roundcube v0.1.1: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Introduced playbook-based role dependencies and removed hard-dependencies on
  optional roles. For this reason the role variable ``roundcube__dependencies``
  was removed too. If no or only individual dependencies are required simply
  adjust the playbook accordingly. [ganto_]

- Converted documentation/Changelog to a new format. [ganto_]


debops-contrib.roundcube v0.1.0 - 2016-06-14
--------------------------------------------

Added
~~~~~

- Initial release of Roundcube 1.1.5 with SQLite and MySQL support. [ganto_]
