Changelog
=========

.. include:: includes/all.rst

**debops.php**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.php master`_ - unreleased
---------------------------------

.. _debops.php master: https://github.com/debops/ansible-php/compare/v0.2.7...master


`debops.php v0.2.7`_ - 2017-08-14
---------------------------------

.. _debops.php v0.2.7: https://github.com/debops/ansible-php/compare/v0.2.6...v0.2.7

Added
~~~~~

- Introduce :envvar:`php__included_packages` and enable filtering of PHP
  packages which are shipped with the ``php-common`` APT package. The
  variable is already defined according to the PHP packages shipped with
  the supported distribution releases. [ganto_]

Fixed
~~~~~

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]


`debops.php v0.2.6`_ - 2017-02-21
---------------------------------

.. _debops.php v0.2.6: https://github.com/debops/ansible-php/compare/v0.2.5...v0.2.6

Changed
~~~~~~~

- The ``php-filter-packages.sh`` script will update APT package cache before
  listing the PHP-related packages. This should fix issues with the PHP
  installation when the APT cache has not been properly updated. [drybjed_]


`debops.php v0.2.5`_ - 2017-02-21
---------------------------------

.. _debops.php v0.2.5: https://github.com/debops/ansible-php/compare/v0.2.4...v0.2.5

Added
~~~~~

- Allow the ``webadmins`` UNIX system group to reload the ``php-fpm`` service
  if needed using ``sudo``. [carlalexander, drybjed_]

- The ``php-cli`` command will not set any hard memory limits during execution
  of PHP scripts. [carlalexander]

Changed
~~~~~~~

- Move the list of all PHP packages requested for installation to a default
  variable. [drybjed_]

- Set the environment for the configuration synchronization script to avoid
  idempotency issues. [drybjed_]

Fixed
~~~~~

- Fix an issue with the package filter script returning an empty package name.
  [drybjed_]


`debops.php v0.2.4`_ - 2016-10-19
---------------------------------

.. _debops.php v0.2.4: https://github.com/debops/ansible-php/compare/v0.2.3...v0.2.4

Added
~~~~~

- :envvar:`php__dependent_configuration`. [ypid_]

Changed
~~~~~~~

- Redesign the method of selecting the correct PHP package versions. Now role
  checks what packages are available and picks the correct package name using
  a script before requesting their installation. [drybjed_]

Fixed
~~~~~

- Ensure that the ``"php" + php__version`` package is installed so that
  packages with alternative package dependencies work correctly. [ypid_]

- Fixed deprecation warning of Ansible 2 when all tasks of the role are
  skipped. [ypid_]


`debops.php v0.2.3`_ - 2016-08-09
---------------------------------

.. _debops.php v0.2.3: https://github.com/debops/ansible-php/compare/v0.2.2...v0.2.3

Added
~~~~~

- :envvar:`php__reset` option which causes the role reevaluate the
  preferred PHP version and remove older PHP versions on the next Ansible run
  when set to ``True``. [ypid_]

- Expose all base directory paths via Ansible facts. [ypid_]

Fixed
~~~~~

- Detection of ``ansible_local.php.long_version`` when the first entry for
  :envvar:`php__version_preference` is not available on the system. [ypid_]

- Compatibility with PHP versions before 5.6.0. [ypid_]


`debops.php v0.2.2`_ - 2016-07-27
---------------------------------

.. _debops.php v0.2.2: https://github.com/debops/ansible-php/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Allow creation of user accounts without creating their home directories. [drybjed_]

- Fix wrong ``php-fpm`` parameter names in pool templates. [drybjed_]


`debops.php v0.2.1`_ - 2016-07-19
---------------------------------

.. _debops.php v0.2.1: https://github.com/debops/ansible-php/compare/v0.2.0...v0.2.1

Added
~~~~~

- Add default variable with configuration for debops.apt_preferences_ role,
  and update the playbook to include the new role dependency. [drybjed_]

Changed
~~~~~~~

- Status of the :envvar:`php__sury` variable is now preserved in Ansible local facts.
  If the custom repository is enabled, it will stay enabled even when the user
  removes the variable from inventory. [drybjed_]

- Update the PHP SAPI config synchronization script to support older PHP5
  installations on Debian Wheezy. [drybjed_]


`debops.php v0.2.0`_ - 2016-07-11
---------------------------------

.. _debops.php v0.2.0: https://github.com/debops/ansible-php/compare/v0.1.0...v0.2.0

Added
~~~~~

- Added support for PHP7 installed from OS releases that have it available.
  [mbarcia]

- Role now exposes an additional :envvar:`php__dependent_packages` list which can be
  used by other Ansible roles to install PHP packages for the current version
  without the need for the other roles to know what PHP version is installed.
  [drybjed_]

- The ``item.state`` parameter in PHP-FPM pool configuration can be used to
  generate or remove pools conditionally. [drybjed_]

- Role now exposes more ``php__*_pools`` lists to allow for better pool
  management from Ansible inventory as well as creation of pools by other
  Ansible roles. [drybjed_]

- Add new :file:`env/` subdirectory for a custom ``debops.php/env`` Ansible role
  which prepares environment usable by other Ansible roles before the main role
  is executed. Some tasks from the main role have been moved there, thus
  ``debops.php/env`` role is mandatory and needs to be added to all playbooks
  that use ``debops.php`` role. [drybjed_]

- Add an example Ansible playbook in :file:`docs/playbooks/` directory. [drybjed_]

- Add custom configuration for debops.logrotate_ Ansible role in default
  variables. [drybjed_]

- Add new :file:`php.ini` configuration which uses a separate :file:`/etc/php/ansible/`
  directory with generated configuration files, which are then symlinked to
  different PHP server API :file:`conf.d/` directories, similar to how Debian
  packages handle PHP extensions. The role allows easy creation of custom
  configuration files using a separate YAML list. Configuration is applied to
  all server APIs at the same time. [drybjed_]

- Add tags to some tasks in the role to allow faster changes to PHP
  configuration or PHP-FPM pools. [drybjed_]

- Add configuration of :file:`/etc/php{5,/7.0}/fpm/php-fpm.conf` configuration file
  and its corresponding variables. [drybjed_]

- Add tasks that create users and groups to allow creation of new PHP-FPM pools
  without errors. [drybjed_]

- Add upgrade notes. [drybjed_]

Changed
~~~~~~~

- Renamed all role variables from ``php5_*`` to ``php__*`` to make role
  universal between major PHP versions and put its variables in a separate
  namespace. [mbarcia]

- Converted Changelog to a new format. [drybjed_]

- Role now detects what PHP package versions are available and installs the
  highest one available. An optional Ondřej Surý APT/PPA repository can be
  enabled on Debian or Ubuntu distributions to provide newer version of
  packages if desired. [drybjed_]

- The ``php__pool_default`` variable which defines the default PHP-FPM pool has
  been renamed to :envvar:`php__pool_www_data`. It is now included in the
  :envvar:`php__default_pools` list. [drybjed_]

- Some role tasks will only be activated by the presence of ``fpm`` package in
  :envvar:`php__server_api_packages` list. This allows for management of PHP
  environment without PHP-FPM installed. [drybjed_]

- The default :file:`/etc/php{5,7.0}/fpm/pool.d/www.conf` pool is now diverted to
  a separate file instead of being removed, to allow unattended package
  upgrades. [drybjed_]

- Role variables related to :file:`php.ini` configuration have been renamed from
  ``php__*`` prefix to ``php__ini_*`` prefix to ensure better separation of
  different configuration options. [drybjed_]

- The timezone configuration is now based on the ``ansible_local.timezone``
  Ansible fact, managed by debops.core_ role, instead of reading the
  :file:`/etc/timezone` file directly. [drybjed_]

- Role variables related to PHP-FPM pool configuration have been renamed from
  ``php__*`` to ``php__fpm_*`` to better separate them from other variables.
  [drybjed_]

- Update documentation and Changelog. [drybjed_]

- Change the tasks that perform diversion to check the :command:`dpkg-divert` list
  instead of relying on the existence of diverted files. This helps with
  upgrades from older ``debops.php5`` role. [drybjed_]

Removed
~~~~~~~

- The ``php__version`` variable cannot be set directly; instead the available
  PHP version is detected at role execution and stored in Ansible local facts
  to ensure idempotency. The autodetected PHP version can be influenced by
  order of the package names in :envvar:`php__version_preference` list. [drybjed_]

- The :file:`/etc/php{5,7.0}/fpm/pool-available.d/` directory used to hold the
  generated pool configuration files has been removed. The Debian PHP packages
  don't support this approach, and switch to the ``item.state`` parameter makes
  this method redundant. [drybjed_]

- The ``item.enabled`` parameter in pool configuration has been replaced by
  ``item.state``. [drybjed_]

- The handler flush at the end of the role task list has been removed.
  [drybjed_]

- Role does not configure its own ``logrotate`` configuration anymore. The
  debops.logrotate_ role is used instead. An example usage can be found in
  the provided playbook. [drybjed_]

- The direct configuration of :file:`php.ini` files in different PHP Server API
  directories has been removed to avoid conflicts during package updates, because
  these files are managed using ``ucf`` which does not support file diversion.
  This also allows usage of default :file:`php.ini` configuration options where
  possible and only override the important ones in a different file. [drybjed_]


debops.php v0.1.0 - 2016-06-01
------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]
