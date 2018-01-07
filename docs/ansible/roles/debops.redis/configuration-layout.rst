Configuration layout
====================

.. contents:: Sections
   :local:


Redis Server configuration files
--------------------------------

The Redis Server is designed to be configured without the need for a restart.
It can also rewrite its own configuration files. The ``debops.redis`` role is
designed with this in mind.

The default configuration file included in the ``redis-server`` package is
diverted after installation to preserve the default values and avoid rewriting
issues on a package upgrade. The default configuration is copied back in place
afterwards to use the default Debian values.

The role configuration is split into two files:

- the :file:`/etc/redis/ansible-redis-static.conf` is a normal Redis Server
  configuration file which is included in the main :file:`/etc/redis/redis.conf`
  configuration to provide the desired values. It contains configuration
  parameters that are not supported by the Redis dynamic configuration options,
  or require a service restart to be effective, like interface/port
  configuration. When this file is changed, the role updates the ``include``
  line in the main Redis configuration file so that the inclusion is as late as
  possible - this way parameters added by Redis in the main configuration file
  should be automatically overridden by :file:`ansible-redis-static.conf`.

- the :file:`/etc/redis/ansible-redis-dynamic.conf` is a Bash script which
  configures the Redis Server using ``redis-cli`` command, while the service is
  running. When all parameters are configured, the main Redis configuration
  file is rewritten to save the changes. Modifications to parameters stored in
  this file don't require a Redis Server restart.

Configuration of both files is stored in
:envvar:`redis__server_combined_configuration` YAML dictionary. Check the
:ref:`redis__ref_server_configuration` for more details.

The :envvar:`redis__server_static_options` list is used to determine which Redis
Server parameters are static, and which are dynamic. This configuration layout
might not be a 100% reliable solution. If you find any issues with it, please
let us know.


Redis Sentinel configuration files
----------------------------------

The Redis Sentinel modifies its own configuration file as needed during its
operation, therefore it's not a suitable target for Ansible management. The
default configuration file included in the Debian package contains
configuration that might be false in the existing environment. Because a single
Sentinel instance can manage multiple Redis master servers, use of the default
configuration provided by the package is not considered.

The role diverts the default :file:`/etc/redis/sentinel.conf` configuration file so
that subsequent package updates won't modify it. Next, a new configuration file
is generated from scratch, with parameters relevant to the configuration from
the role variables. If the Redis instance is running in a standalone mode, no
Redis master server will be included in the Sentinel configuration (the daemon
works fine without one). If a clustered mode is enabled, by default the host
indicated by the :envvar:`redis__server_master_host` variable will be configured as
the Redis master server.

After the initial configuration, if the :file:`sentinel.conf` configuration file
exists, it won't be modified again to not destroy the cluster information
stored in it by the ``redis-sentinel`` daemon. Therefore, reconfiguration of
the Redis Sentinel installation by ``debops.redis`` role is not supported
without additional steps.
