Default variable details
========================

Some of ``debops.redis_server`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _redis_server__ref_instances:

redis_server__instances
-----------------------

The role can manage multiple Redis Server instances on a single host via the
``redis_server__*_instances`` default variables. Each variable is a list of
YAML dictionaries, each dictionary defines an instance of Redis managed by
:command:`systemd` unit template.

Configuration specified in the instance YAML dictionary is parsed by the role
and used to generate the final configuration which is then used to manage the
Redis instances (see :ref:`redis_server__ref_config_pipeline`).

Multiple dictionaries with the same ``name`` parameter will be merged together;
this can be used to override previously defined instance configuration without
copying everything to the Ansible inventory.

Examples
~~~~~~~~

Define multiple Redis Server instances:

.. literalinclude:: examples/multiple_instances.yml
   :language: yaml

Modify existing instance configuration:

.. literalinclude:: examples/modify_main_instance.yml
   :language: yaml

Syntax
~~~~~~

Each entry can contain specific parameters:

``name``
  Required. THe name of a given Redis instance. This parameter is used as an
  anchor for merging of multiple YAML dictionaries that specify Redis instances
  together.

  The instance name ``main`` is significant and used in Ansible local fact
  script and the password script to denote the "default" Redis instance if none
  is specified.

``port``
  Required. The TCP port on which a given instance listens for network
  connections. Only ports defined in the instance list will be included in the
  automatically managed firewall configuration.

``state``
  Optional. If not specified or ``present``, a given Redis instance will be
  created or managed by the role. If ``absent``, a given instance will be
  removed by the role. If ``ignore``, a given instance entry will not be
  included in the configuration.

``pidfile``
  Optional. Absolute path to a PID file of a given Redis instance. If not
  specified, the role will generate one based on the instance name.

``unixsocket``
  Optional. Absolute path to an UNIX socket file of a given Redis instance. If
  not specified, the role will generate one based on the instance name.

``bind``
  Optional. A string or a YAML list of IP addresses to which a given Redis
  instance should bind to to listen for network connections. If not specified,
  the instance will bind on the IP addresses specified in the
  :envvar:`redis_server__bind` variable, by default ``localhost``.

``dbfilename``
  Optional. Name of the Redis database file which will contain the persisten
  storage, stored in the :file:`/var/lib/redis/` directory. If not specified,
  the role will generate the name based on the instance name.

``logfile``
  Optional. Absolute path to a log file of a given Redis instance. If not
  specified, the role will generate one based on the instance name.

``syslog_ident``
  Optional. A short string that identifies a given Redis instance in the syslog
  stream. If not specified, the role will generate one based on the instance
  name.

``requirepass``
  Optional. Plaintext password which will be required by Redis to allow certain
  operations. If not specified, the value of the
  :envvar:`redis_server__auth_password` will be used automatically.

``systemd_override``
  Optional. An YAML text block that contains :command:`systemd` unit
  configuration entries. This can be used to override the configuration of
  a Redis instance managed by :command:`systemd`.

``master_host`` and ``master_port``
  Optional. The FQDN address of the host with the Redis master instance, and
  its TCP port. If these parameters are set, a given Redis instance will be
  configured as a slave of the specified Redis master on the initial
  configuration, but not subsequent ones.

Other configuration options for a given Redis instance should be specified in
the ``redis_server__*_configuration`` variables. Some of the instance
parameters like ``port`` are used in other parts of the role and should be
overridden only on the list of instances.


.. _redis_server__ref_configuration:

redis_server__configuration
---------------------------

The ``redis_server__*_configuration`` variables define the configuration of the
Redis Server instances. A Redis Server instance consists of a set of
configuration files in :file:`/etc/redis/<instance>/` subdirectory, as well as
:command:`systemd` service template configuration.
See :ref:`redis_server__ref_config_pipeline` for more details.

Examples
~~~~~~~~

Define additional instance configuration:

.. literalinclude:: examples/instance_configuration.yml
   :language: yaml

Syntax
~~~~~~

Each variable contains a list of YAML dictionaries, each dictionary defines
a Redis Server instance using specific parameters:

``name``
  Required. Name of a given Redis Server instance, should be a short
  alphanumeric string. This parameter is used as an anchor to merge multiple
  instance entries together.

``port``
  Required. The TCP port on which a given instance listens for network
  connections.

``state``
  Optional. If not specified or ``present``, a given Redis Server instance will
  be created and/or managed on a given host. If ``absent``, a given Redis
  Server instance will be stopped and its configuration will be removed. If
  ``ignore``, a given configuration entry will be ignored by the role during
  the Ansible run; this can be used to conditionally enable or disable instance
  options if needed.

``requirepass``
  Optional. Plaintext password which will be required by Redis to allow certain
  operations.

``systemd_override``
  Optional. An YAML text block that contains :command:`systemd` unit
  configuration entries. This can be used to override the configuration of
  a Redis instance managed by :command:`systemd`.

``master_host`` and ``master_port``
  Optional. The FQDN address of the host with the Redis master instance, and
  its TCP port. If these parameters are set, a given Redis instance will be
  configured as a slave of the specified Redis master on the initial
  configuration, but not subsequent ones.

``options``
  A list of configuration options for the Redis Server instance. The
  ``options`` lists from multiple instance configuration entries are merged
  together. Each element of the ``options`` list is a YAML dictionary with
  specific parameters:

  ``name``
    Redis Server parameter name. Parameter names containing hypens should be
    quoted to avoid any issues with YAML parsing.

  ``value``
    Redis Server parameter value. It can be a number, a string or a list of
    strings. If a list is used, by default the configuration file will contain
    multiple parameters with the same name and values specified on separate
    lines. you can also use the Python ``True`` and ``False`` values to
    represent booleans.

  ``state``
    Optional. If not specified or ``present``, a given parameter will be
    present in the generated configuration. If ``absent``, a given parameter
    will be removed from the configuration.

  ``dynamic``
    Optional, bollean. If ``True``, a given parameter will be marked as
    a "dynamic" Redis configuration and will not be included in the static
    configuration file. Instead, it will be applied dynamically via
    a configuration script during deployment.

  ``multiple``
    Optional, boolean. If ``False``, and the parameter is not dynamic, and it's
    a list, the values will be concatenated into one string, separated by
    spaces. This is required by some of the Redis Server configuration options,
    for example ``bind``.

  If the ``name`` and ``value`` parameters are not present, each key of the
  YAML dictionary will be interpreted as a separate Redis Server parameter.
  This can be used as a shorthand to define Redis Server parameters, but for
  more complicated parameters (dynamic, with custom requirements), you should
  use the expanded form explained above.
