Changelog
=========

**debops.php**

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.php master`_ - unreleased
---------------------------------

.. _debops.php master: https://github.com/debops/ansible-php/compare/v0.2.0...master


`debops.php v0.2.0`_ - unreleased
---------------------------------

.. _debops.php v0.2.0: https://github.com/debops/ansible-php/compare/v0.1.0...v0.2.0

Added
~~~~~

- Added support for PHP7 installed from OS releases that have it available.
  [mbarcia]

- Role now exposes an additional ``php__dependent_packages`` list which can be
  used by other Ansible roles to install PHP packages for the current version
  without the need for the other roles to know what PHP version is installed.
  [drybjed]

- The ``item.state`` parameter in PHP-FPM pool configuration can be used to
  generate or remove pools conditionally. [drybjed]

- Role now exposes more ``php__*_pools`` lists to allow for better pool
  management from Ansible inventory as well as creation of pools by other
  Ansible roles. [drybjed]

- Add new ``env/`` subdirectory for a custom ``debops.php/env`` Ansible role
  which prepares environment usable by other Ansible roles before the main role
  is executed. Some tasks from the main role have been moved there, thus
  ``debops.php/env`` role is mandatory and needs to be added to all playbooks
  that use ``debops.php`` role. [drybjed]

- Add an example Ansible playbook in ``docs/playbooks/`` directory. [drybjed]

- Add custom configuration for ``debops.logrotate`` Ansible role in default
  variables. [drybjed]

- Add new ``php.ini`` configuration which uses a separate ``/etc/php/ansible/``
  directory with generated configuration files, which are then symlinked to
  different PHP Server API ``conf.d/`` directories, similar to how Debian
  packages handle PHP extensions. The role allows easy creation of custom
  configuration files using a separate YAML list. Configuration is applied to
  all Server APIs at the same time. [drybjed]

- Add tags to some tasks in the role to allow faster changes to PHP
  configuration or PHP-FPM pools. [drybjed]

- Add configuration of ``/etc/php{5,/7.0}/fpm/php-fpm.conf`` configuration file
  and its corresponding variables. [drybjed]

Changed
~~~~~~~

- Renamed all role variables from ``php5_*`` to ``php__*`` to make role
  unversal between major PHP versions and put its variables in a separate
  namespace. [mbarcia]

- Converted Changelog to a new format. [drybjed]

- Role now detects what PHP package versions are available and installs the
  highest one available. An optional Ondřej Surý APT/PPA repository can be
  enabled on Debian or Ubuntu distributions to provide newer version of
  packages if desired. [drybjed]

- The ``php__pool_default`` variable which defines the default PHP-FPM pool has
  been renamed to ``php__pool_www_data``. It is now included in the
  ``php__default_pools`` list. [drybjed]

- Some role tasks will only be activated by the presence of ``fpm`` package in
  ``php__server_api_packages`` list. This allows for management of PHP
  environment without PHP-FPM installed. [drybjed]

- The default ``/etc/php{5,7.0}/fpm/pool.d/www.conf`` pool is now diverted to
  a separate file instead of being removed, to allow unattended package
  upgrades. [drybjed]

- Role variables related to ``php.ini`` configuration have been renamed from
  ``php__*`` prefix to ``php__ini_*`` prefix to ensure better separation of
  different configuration options. [drybjed]

- The timezone configuration is now based on the ``ansible_local.timezone``
  Ansible fact, managed by ``debops.core`` role, insead of reading the
  ``/etc/timezone`` file directly. [drybjed]

- Role variables related to PHP-FPM pool configuration have been renamed from
  ``php__*`` to ``php__fpm_*`` to better separate them from other variables.
  [drybjed]

- Update documentation and Changelog. [drybjed]

Removed
~~~~~~~

- The ``php__version`` variable cannot be set directly; instead the available
  PHP version is detected at role execution and stored in Ansible local facts
  to ensure idempotency. The autodetected PHP version can be influenced by
  order of the package names in ``php__version_preference`` list. [drybjed]

- The ``/etc/php{5,7.0}/fpm/pool-available.d/`` directory used to hold the
  generated pool configuration files has been removed. The Debian PHP packages
  don't support this approach, and switch to the ``item.state`` parameter makes
  this method redundant. [drybjed]

- The ``item.enabled`` parameter in pool configuration has been replaced by
  ``item.state``. [drybjed]

- The handler flush at the end of the role task list has been removed.
  [drybjed]

- Role does not configure its own ``logrotate`` configuration anymore. The
  ``debops.logrotate`` role is used instead. An example usage can be found in
  the provided playbook. [drybjed]

- The direct configuration of ``php.ini`` files in different PHP Server API
  directories has been removed to avoid confict during package updates, because
  these files are managed using ``ucf`` which does not support file diversion.
  This also allows usage of default ``php.ini`` configuration options where
  possible and only override the important ones in a different file. [drybjed]


debops.php v0.1.0 - 2016-06-01
------------------------------

Added
~~~~~

- Add Changelog. [drybjed]
