Default variable details
========================

Some of ``debops.php`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 1


.. _php__ref_packages:

php__packages
-------------

The :envvar:`php__packages`, :envvar:`php__group_packages`, :envvar:`php__host_packages` and
:envvar:`php__dependent_packages` lists can be used to install APT packages. The role
automatically prepends the package names with correct prefix (``php5-`` or
``php7.0-``) to install packages for currently active PHP version. Because of
that you should only use these lists to install PHP-related packages.

The packages with names in the form:

- ``php-*``

- ``php5-*``

- ``php7.0-*``

will be detected correctly. Any other package names will have the current PHP
version prepended to their name, which might result in incorrect installation
requests.

Examples
~~~~~~~~

Install support for the MariaDB/MySQL and PostgreSQL databases for the current
PHP version:

.. code-block:: yaml

   php__packages: [ 'mysql', 'pgsql' ]

Install support for the PEAR repository:

.. code-block:: yaml

   php__packages: [ 'php-pear' ]


.. _php__ref_configuration:

php__configuration
------------------

The management of the :file:`php.ini` configuration is done using a set of YAML
lists, named :envvar:`php__configuration`, :envvar:`php__group_configuration` and
:envvar:`php__host_configuration`. Each element of a list is a YAML dictionary with
certain parameters.

The configuration is designed to allow easy creation of multiple configuration
files located in :file:`/etc/php{5,/7.0}/` directories. By default, all files are
created in the :file:`/etc/php{5,/7.0}/ansible/` directory with the ``.ini``
extension, and symlinked to the respective PHP SAPI configuration directories.
If you need, you can create the configuration files directly in the PHP SAPI
directories as well.

The role recognizes the parameters below:

``filename``
  Required. Name of the file to store the configuration data, for example
  ``00-ansible``. The ``.ini`` extension is added automatically at the end.

``path``
  Optional. Change the default path where a given configuration file should be
  created, relative to :file:`/etc/php{5,/7.0}/`. By default this value is
  :command:`ansible/`. You need to add the ``/`` character at the end of the path for
  the role to work correctly.

``sections``
  Optional. List of YAML dictionaries, each one describing a part of the given
  configuration file.

The parameters below can be specified either in the main YAML dictionary, or in
one of the YAML dictionaries on the ``sections`` list:

``name``
  Optional. An INI section name, for example ``PHP`` which will be written as
  ``[PHP]`` in the configuration file.

``options``
  A YAML text block with :file:`php.ini` configuration options specified in the INI
  configuration file format.

``comment``
  Optional. A custom comment added before a specified configuration.

``state``
  Optional, either ``present`` or ``absent``. If not specified or ``present``,
  a given configuration file or its section will be created. If ``absent``,
  a given configuration file or section will be removed.

Examples
~~~~~~~~

Create custom configuration file symlinked to all PHP SAPI directories:

.. code-block:: yaml

   php__configuration:
     - filename: '10-custom'
       name: 'PHP'
       options: |
         display_errors = On

Create custom configuration file with multiple sections directly in PHP-FPM
directory:

.. code-block:: yaml

   php__host_configuration:
     - filename: '50-custom'
       path: 'fpm/conf.d/'
       sections:

         - name: 'CLI server'
           options: |
             cli_server.color = On

         - name: 'mail function'
           options: |
             SMTP = smtp.{{ ansible_domain }}
             smtp_port = 25


.. _php__ref_pools:

php__pools
----------

The :envvar:`php__pools`, :envvar:`php__group_pools`, :envvar:`php__host_pools` and
:envvar:`php__dependent_pools` lists can be used to create PHP-FPM pools. Each list
entry is a YAML dictionary with keys and values that represent options in the
pool configuration file (with some additional parameters used by the role
itself).

Most of the pool parameters have their corresponding default variables in the
``php__fpm_*`` namespace. To use them in the pool configuration, strip the
``php__fpm_`` prefix from their variable name, for example:

.. code-block:: yaml

   php__fpm_access_log: True

   php__pools:
     - name: 'www-data'
       access_log: False

Below are some parameters that don't have their corresponding defaults or are
otherwise different:

``name``
  Required. Name of the PHP-FPM pool.

``state``
  Optional. If not specified or ``present``, the PHP-FPM pool will be created.
  If specified and ``absent``, the PHP-FPM pool will be removed.

``user``
  Optional. Name of the system user account which will be used to execute the
  given PHP-FPM pool. This account needs to exist before the pool will start
  correctly. If not specified, the ``item.name`` value will be used.

``group``
  Optional. The main group in which the PHP-FPM pool will be running in. If not
  specified, the ``item.name`` value will be used instead.

``owner``, ``home``
  Optional. If specified, role will create an user account with specified home
  directory before restarting the PHP-FPM service. This permits easy creation
  of new PHP-FPM pools on separate user accounts. Ideally the ``item.owner``
  value should be the same as ``item.user`` or ``item.name``. It's defined
  separately to better control user/group creation process.

``system``
  Optional, boolean. If defined and ``True``, the account and group will be
  created as a "system" account with UID/GID < 1000; this is the default. If
  ``False``, the created user and group will have "normal" UID/GID selected.

``listen``
  Optional. Path to the PHP-FPM socket or IP:port on which a given pool should
  listen for connections. By default it's autogenerated in the format:
  :file:`/run/php{5,7.0}-fpm-{{ item.name }}.sock`.

``listen_owner``
  Optional. The system user that will be the owner of the PHP-FPM socket. This
  should be the username of the webserver account, so that it can use the
  socket to communicate with the PHP-FPM process. This account needs to exist
  before the PHP-FPM process is started (the ``www-data`` account is created
  by default on Debian/Ubuntu systems). If not specified, the
  ``php__fpm_listen_owner`` value will be used instead.

``listen_group``
  Optional. The system group that will be the primary group of the PHP-FPM
  socket. This should be the group that the webserver belongs to, so that it
  can use the socket to communicate with the PHP-FPM process. This group needs
  to exist before the PHP-FPM process is started (the ``www-data`` group is
  created by default on Debian/Ubuntu systems). If not specified, the
  ``php__fpm_listen_group`` value will be used instead.

``listen_acl_users``
  Optional. Set POSIX Access Control Lists. If specified, listen_owner is
  ignored. The value must be a list of names.

``listen_acl_groups``
  Optional. Set POSIX Access Control Lists. If specified, listen_group is
  ignored. The value must be a list of names.

``listen_mode``
  Optional. The permissions applied to the PHP-FPM pool sockets.
  If not specified, the ``php__fpm_listen_mode`` value will be used instead.

``listen_backlog``
  Optional. The limit for socket connection backlog. If you tune this
  parameter, you should also consider sysctl parameters
  ``net.ipv4.tcp_max_syn_backlog``, ``net.ipv4.ip_local_port_range``,
  ``net.ipv4.tcp_tw_reuse`` and ``net.core.somaxconn``. If not specified,
  the ``php__fpm_listen_backlog`` will be used instead.

``environment``
  Optional. A YAML dictionary with custom environment variables that should be
  specified in the PHP-FPM pool. Each dictionary key is a variable name and
  dictionary value is the variable value.

``php_flags``
  Optional. A YAML dictionary with custom :file:`php.ini` flags that should be
  defined in the PHP-FPM pool. Each dictionary key is the flag name, and each
  dictionary value is the flag value.

``php_values``
  Optional. A YAML dictionary with custom :file:`php.ini` values that should be
  defined in the PHP-FPM pool. Each dictionary key is the value name, and each
  dictionary value is the value contents.

``php_admin_flags``
  Optional. A YAML dictionary with custom :file:`php.ini` admin flags that should
  be defined in the PHP-FPM pool. Each dictionary key is the admin flag name,
  and each dictionary value is the admin flag value.

``php_admin_values``
  Optional. A YAML dictionary with custom :file:`php.ini` admin values that should
  be defined in the PHP-FPM pool. Each dictionary key is the admin value name,
  and each dictionary value is the admin value contents.

``open_basedir``
  Optional. String or list of paths which can be accessed by the PHP
  interpreter. By default not set.

Examples
~~~~~~~~

Create a new PHP-FPM pool with custom user account:

.. code-block:: yaml

   php__host_pools:
     - name: 'custom-php-app'
       owner: 'custom-php-app'
       home: '/srv/custom-php-app'

Modify default PHP-FPM pool with custom environment variables:

.. code-block:: yaml

  php__default_pools:
    - name: 'www-data'
      environment:
        HOME: '/var/www'
        MAIL: 'root@{{ ansible_domain }}'

Remove the default PHP-FPM pool (you should have at least 1 pool configured,
otherwise the PHP-FPM process manager won't start correctly):

.. code-block:: yaml

   php__default_pools:
     - name: 'www-data'
       state: 'absent'
