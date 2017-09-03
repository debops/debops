.. _roundcube__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops-contrib.roundcube**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is ganto_.

Refer to the :ref:`roundcube__ref_upgrade_notes` when you intend to upgrade to a
new release of this role.


`debops-contrib.roundcube master`_ - unreleased
-----------------------------------------------

.. _debops-contrib.roundcube master: https://github.com/debops-contrib/ansible-roundcube/compare/v0.2.0...master


`debops-contrib.roundcube v0.2.0`_ - 2017-08-28
-----------------------------------------------

.. _debops-contrib.roundcube v0.2.0: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.3...v0.2.0

Added
~~~~~

- Added new soft dependency on debops.ferm_ to the example playbook. [ganto_]

- Added new soft dependency on debops.apt_preferences_ to the example playbook
  to satisfy possible package pinning requirements of the debops.nginx_ and
  debops.php_ roles. [ganto_]

- Added new soft dependency on debops.logrotate_ to the example playbook to
  handle logfile rotation of PHP-FPM. [ganto_]

- New configuration variables :envvar:`roundcube__shell` and
  :envvar:`roundcube__comment` to customize the Roundcube system account. [ganto_]

- New configuration variables :envvar:`roundcube__database_password_path` and
  :envvar:`roundcube__database_name` for easier customization of the database
  setup. [ganto_]

- Install PHP packages which cannot be satisfied by the APT package manager
  via PHP's own :command:`composer` dependency manager. [ganto_]

- Run post-install script provided by upstream which downloads the required
  Javascript libraries served to the Web browsers. [ganto_]


Changed
~~~~~~~

- Set default Roundcube version to 1.3.0. [ganto_]

- Adjusted the debops.nginx_ configuration to make use of the role's dependent
  variables which required minor format changes and variable name adjustments to
  correspond to the DebOps naming conventions:
  ``roundcube__nginx_server`` → :envvar:`roundcube__nginx__dependent_servers`
  ``roundcube__nginx_upstream_php5`` → :envvar:`roundcube__nginx__dependent_upstreams`
  [ganto_]

- Make use of the debops.mariadb_ dependent variables in the example playbook.
  [ganto_]

- Updated PHP role dependency from ``debops.php5`` to the more capable debops.php_.
  This changed the format and name of the following variables:
  ``roundcube__php5_packages`` → :envvar:`roundcube__php__dependent_packages`
  ``roundcube__php5_pool`` → :envvar:`roundcube__php__dependent_pools`
  [ganto_]

- Renamed ``roundcube__extra_packages`` to :envvar:`roundcube__packages` to be
  consistent with other DebOps roles. [ganto_]

- Changed default configuration of :envvar:`roundcube__www` from
  :file:`/srv/www/{{ roundcube__user }}` to :file:`/srv/www` to be more
  consistent with other system-wide Web applications. [ganto_]


Fixed
~~~~~

- Fixed definition of :envvar:`roundcube__home` and :envvar:`roundcube__src` in
  cases where the local facts defined by debops.core_ are not available. [ganto_]


Removed
~~~~~~~

- Remove support for Debian (oldoldstable) wheezy. [ganto_]


`debops-contrib.roundcube v0.1.3`_ - 2017-07-26
-----------------------------------------------

.. _debops-contrib.roundcube v0.1.3: https://github.com/debops-contrib/ansible-roundcube/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Set default version to 1.1.9. [ganto_]


Fixed
~~~~~

- Fix documentation build error due to deleted link definition to deprecated
  ``debops.php5`` role repository. [ganto_]
- Probe if :envvar:`roundcube__domain` is a string and construct :envvar:`roundcube__git_checkout` accordingly.  [cultcom]


`debops-contrib.roundcube v0.1.2`_ - 2017-03-09
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


`debops-contrib.roundcube v0.1.1`_ - 2016-08-03
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
