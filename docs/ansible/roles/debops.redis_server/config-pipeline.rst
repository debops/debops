.. _redis_server__ref_config_pipeline:

Redis Server configuration pipeline
===================================

The default Redis Server installation in Debian Jessie and Debian Stretch
supports only 1 instance of Redis per host. The pacakges in Debian Buster and
the ``stretch-backports`` repository support multiple instances by using
a single :file:`/etc/redis/redis-<instance>.conf` configuration file per
a :command:`systemd` instance. However, due to the Redis modifying its own
configuration file on the fly, using a single :file:`redis.conf` configuration
file does not work well with an Ansible-based approach to configuration.

The solution to this problem implemented in :ref:`debops.redis_server` role is
usage of a separate :file:`/etc/redis/<instance>/` directory for each Redis
Server instance. This allows usage of multiple configuration files and even
scripts for each Redis Server instance, with configuration applied dynamically
at runtime. The :file:`redis.conf` configuration file is not touched directly
by Ansible, apart from ensuring that additional configuration file with
Ansible-generated parameters is included at the end. This ensures
idempotency and allows Ansible and Redis to work together.


Configuration variables
-----------------------

The :ref:`debops.redis_server` Ansible role exposes a set of default variables
that can be used to define and modify Redis configuration per instance.
Configuration defined in each one is merged together in the
:envvar:`redis_server__combined_configuration` using a special filter plugin.
Multiple configuration entries defined in the format of the
:ref:`redis_server__ref_configuration` parameters are merged together,
therefore there's no need to copy everything to the Ansible inventory.

The variables are merged in the following order:

- the :envvar:`redis_server__default_base_options` and the
  :envvar:`redis_server__base_options` hold the default parameters applied to
  all of the Redis Server instances on a particular host. These variables can
  be used to override options applied to all instances when needed.

- the :envvar:`redis_server__default_instances` and the all/group/host variant of
  the same variable are used to generate configuration for each instance, which
  is then put in the configuration pipeline via the
  :envvar:`redis_server__default_configuration` variable. Each instance will
  include the base options defined for all instances, and per-instance
  configuration like port, UNIX socket path, optional :command:`systemd`
  overrides, etc.

- the :envvar:`redis_server__default_configuration` and the all/group/host
  variants include the actual configuration used by the role to generate the
  Redis Server configuration files, :command:`systemd` service configuration.
  The variables are joined together in the
  :envvar:`redis_server__combined_configuration` variable which is used in
  varius role tasks and templates. These variables can be used to override
  per-instance configuration if needed.


Configuration file structure
----------------------------

The generated configuration file structure contains the following files:

.. code-block:: none

   /etc/redis
   ├── main/
   │   ├── ansible-redis-dynamic.conf*
   │   ├── ansible-redis-static.conf
   │   └── redis.conf
   ├── second/
   │   ├── ansible-redis-dynamic.conf*
   │   ├── ansible-redis-static.conf
   │   └── redis.conf
   ├── third/
   │   ├── ansible-redis-dynamic.conf*
   │   ├── ansible-redis-static.conf
   │   └── redis.conf
   └── redis.conf

The :file:`ansible-redis-static.conf` files contain static configuration
options for each Redis Server instance. If any options there change, a given
instance is restarted.

The :file:`ansible-redis-dynamic.conf` files are Bash scripts which apply Redis
Server configuration dynamically at runtime, using the ``CONFIG SET`` commands
via the :command:`redis-cli` interface. The ``CONFIG REWRITE`` command is then
executed so that Redis can update its own configuration file; this way the
dynamic configuration is preserved between restarts.

The :file:`redis.conf` configuration files are copies of the original
:file:`/etc/redis/redis.conf` configuration file created when each instance is
initialized. The role assumes that Redis modifies these files dynamically and
doesn't touch them directly, apart from ensuring that an ``include`` line for
the :file:`ansible-redis-static.conf` is present and near the end of the file.
