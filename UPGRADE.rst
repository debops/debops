Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the Changelog for
more details about what has changed.

From debops.php5 role to debops.php role
----------------------------------------

- The ``debops.php5`` role stored the PHP-FPM pool configuration in a custom
  ``/etc/php5/fpm/pool-available.d/`` directory and symlinked the files to the
  ``/etc/php5/fpm/pool.d/`` directory used by PHP-FPM daemon. In ``debops.php``
  this mechanism was dropped and files are generated directly in
  ``/etc/php5/fpm/pool.d/``. Existing files seem to be unaffected by being
  symlinked to the old directory therefore you don't need to replace the
  symlinks with real files manually.

- The ``debops.php`` role has new role dependencies on ``debops.php/env`` and
  ``debops.logrotate``. Refer to the provided playbook for an example usage.

- The different ``/etc/php5/*/php.ini`` configuration files managed by
  ``debops.php5`` role are not managed by ``debops.php`` role anymore and might
  be incomplete. You can replace them with the pristine versions located in:
  ``/usr/share/php5/php.ini-*`` or ``/usr/lib/php/7.0/php.ini-*``.

- All of the role variables have been renamed from ``php5_*`` to ``php__*``.
  Some variables have been further renamed, for example from ``php5_default_*``
  to ``php__fpm_*`` or various variables to ``php__ini_*``. You should check
  the variables used in inventory against the new default variables and update
  accordingly.

- Some of the parameter names in FPM pools were renamed (for example
  ``item.accesslog`` became ``item.aceess_log``). Refer to the list of PHP-FPM
  pool default variables for possible changes and update the pool configuration
  accordingly.

- The package installation changed to not force PHP version in the package
  name. For example, role can now install MariaDB support by specifying
  ``mysql`` package instead of ``php5-mysql``. The list of packages might need
  to be updated if you plan to use different PHP versions.

- The PHP7 version uses different directories than the PHP5 version
  (``/etc/php/7.0/`` vs ``/etc/php5/``). This allows for parallel installation
  of PHP5 and PHP7 on the same host, however the role is designed to only
  manage 1 version at a time. You are advised to recreate the host if
  necessary.
