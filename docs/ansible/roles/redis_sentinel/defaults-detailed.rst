Default variable details
========================

Some of ``debops.redis_sentinel`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _redis_sentinel__ref_instances:

redis_sentinel__instances
-------------------------

The role can manage multiple Redis Sentinel instances on a single host via the
``redis_sentinel__*_instances`` default variables. Each variable is a list of
YAML dictionaries, each dictionary defines an instance of Redis Sentinel
managed by :command:`systemd` unit template.

Configuration specified in the instance YAML dictionary is parsed by the role
and used to generate the final configuration which is then used to manage the
Redis Sentinel instances (see :ref:`redis_sentinel__ref_config_pipeline`).

Multiple dictionaries with the same ``name`` parameter will be merged together;
this can be used to override previously defined instance configuration without
copying everything to the Ansible inventory.

Examples
~~~~~~~~

Define multiple Redis Sentinel instances:

.. literalinclude:: examples/multiple_instances.yml
   :language: yaml

Modify existing instance configuration:

.. literalinclude:: examples/modify_main_instance.yml
   :language: yaml

Syntax
~~~~~~

Each entry can contain specific parameters:

``name``
  Required. The name of a given Redis Sentinel instance. This parameter is used
  as an anchor for merging of multiple YAML dictionaries that specify Redis
  Sentinel instances together.

  The instance name ``main`` is significant and used in Ansible local fact
  script to denote the "default" Redis Sentinel instance if none is specified.

``port``
  Required. The TCP port on which a given instance listens for network
  connections. Only ports defined in the instance list will be included in the
  automatically managed firewall configuration.

``state``
  Optional. If not specified or ``present``, a given Redis Sentinel instance
  will be created or managed by the role. If ``absent``, a given instance will
  be removed by the role. If ``ignore``, a given instance entry will not be
  included in the configuration.

``pidfile``
  Optional. Absolute path to a PID file of a given Redis Sentinel instance. If
  not specified, the role will generate one based on the instance name.

``unixsocket``
  Optional. Absolute path to an UNIX socket file of a given Redis Sentinel
  instance. If not specified, the role will generate one based on the instance
  name.

``bind``
  Optional. A string or a YAML list of IP addresses to which a given Redis
  Sentinel instance should bind to to listen for network connections. If not
  specified, the instance will bind on the IP addresses specified in the
  :envvar:`redis_sentinel__bind` variable, by default ``localhost``.

``logfile``
  Optional. Absolute path to a log file of a given Redis Sentinel instance. If
  not specified, the role will generate one based on the instance name.

``syslog_ident``
  Optional. A short string that identifies a given Redis Sentinel instance in
  the syslog stream. If not specified, the role will generate one based on the
  instance name.

``systemd_override``
  Optional. An YAML text block that contains :command:`systemd` unit
  configuration entries. This can be used to override the configuration of
  a Redis Sentinel instance managed by :command:`systemd`.

Other configuration options for a given Redis Sentinel instance should be
specified in the ``redis_sentinel__*_configuration`` variables. Some of the
instance parameters like ``port`` are used in other parts of the role and
should be overridden only on the list of instances.


.. _redis_sentinel__ref_monitors:

redis_sentinel__monitors
------------------------

Redis Sentinel uses "monitors" to track the state of Redis Server instances.
The monitors can be defined using the ``redis_sentinel__*_monitors`` default
variables; each variable is a list of YAML dictionaries. Multiple entries with
the same ``name`` parameter are combined together, you don't need to copy the
entire entry to the Ansible inventory to modify it.

The Redis Sentinel configuration files are generated only once at the
initialization of a given instance. After that, Redis Sentinel modifies these
files directly, therefore Ansible will not try to change them as long as they
are present. You should prepare an adequate monitor configuration beforehand.

Examples
~~~~~~~~

Define additional monitors for all Redis Sentinel instances:

.. literalinclude:: examples/additional_monitors.yml
   :language: yaml

Syntax
~~~~~~

Each Redis Sentinel monitor entry can be defined using specific parameters:

``name``
  Required. The name of a given monitor. This parameter is used as an anchor to
  combine multiple entries together.

``host``
  Required. FQDN or IP address of the Redis Server master which will be
  monitored.

``port``
  Required. The TCP port on which a given Redis Server master listens for
  connections.

``quorum``
  Required. Number of Redis Sentinel instances that are expected to be in
  agreement about the state of Redis Server that is being monitored. It's
  usually number of Redis Sentinel instances / 2 + 1. This parameter is
  currently not computed automatically.

``password``
  Optional. If not specified, the role will set the value of the
  :envvar:`redis_sentinel__auth_password` as the password used by a given
  monitor to access the Redis Server, as the ``auth-pass`` option.

  If ``False``, the password is not set automatically for a given monitor.

``instance``
  Optional. Name of the Redis Sentinel instance in which to define a given
  monitor. If not specified, the monitor will be defined in all instances on
  a given host.

``state``
  Optional. If not specified or ``present``, a given monitor will be defined by
  the role. If ``absent``, a given monitor will not be defined in the initial
  configuration file. If ``ignore``, a given monitor entry will not be included
  in the configuration and will be ignored by the role.

``notification-script``, ``client-reconfig-script``
  These parameters are automatically configured to point to the custom scripts
  inside of a given Redis Sentinel instance configuration directory. You can
  place custom scripts in the corresponding :file:`notify.d/` and
  :file:`reconfig.d/` subdirectories, they will be executed by Redis Sentinel
  using the :command:`run-parts` command.

All other parameters specified in a given monitor entry will be added as-is in
the Redis Sentinel configuration file.


.. _redis_sentinel__ref_configuration:

redis_sentinel__configuration
-----------------------------

The ``redis_sentinel__*_configuration`` variables define the configuration of
the Redis Sentinel instances. A Redis Sentinel instance consists of a set of
configuration files in :file:`/etc/redis/sentinel-<instance>/` subdirectory, as
well as :command:`systemd` service template configuration.  See
:ref:`redis_sentinel__ref_config_pipeline` for more details.

The Redis Sentinel configuration files are generated only once at the
initialization of a given instance. After that, Redis Sentinel modifies these
files directly, therefore Ansible will not try to change them as long as they
are present.

Examples
~~~~~~~~

Define additional instance configuration:

.. literalinclude:: examples/instance_configuration.yml
   :language: yaml

Syntax
~~~~~~

Each variable contains a list of YAML dictionaries, each dictionary defines
a Redis Sentinel instance using specific parameters:

``name``
  Required. Name of a given Redis Sentinel instance, should be a short
  alphanumeric string. This parameter is used as an anchor to merge multiple
  instance entries together.

``port``
  Required. The TCP port on which a given instance listens for network
  connections.

``state``
  Optional. If not specified or ``present``, a given Redis Sentinel instance
  will be created and/or managed on a given host. If ``absent``, a given Redis
  Sentinel instance will be stopped and its configuration will be removed. If
  ``ignore``, a given configuration entry will be ignored by the role during
  the Ansible run; this can be used to conditionally enable or disable instance
  options if needed.

``systemd_override``
  Optional. An YAML text block that contains :command:`systemd` unit
  configuration entries. This can be used to override the configuration of
  a Redis Sentinel instance managed by :command:`systemd`.

``options``
  A list of configuration options for the Redis Sentinel instance. The
  ``options`` lists from multiple instance configuration entries are merged
  together. Each element of the ``options`` list is a YAML dictionary with
  specific parameters:

  ``name``
    Redis Sentinel parameter name. Parameter names containing hypens should be
    quoted to avoid any issues with YAML parsing.

  ``value``
    Redis Sentinel parameter value. It can be a number, a string or a list of
    strings. If a list is used, by default the configuration file will contain
    multiple parameters with the same name and values specified on separate
    lines. you can also use the Python ``True`` and ``False`` values to
    represent booleans.

  ``state``
    Optional. If not specified or ``present``, a given parameter will be
    present in the generated configuration. If ``absent``, a given parameter
    will be removed from the configuration.

  ``prefix``
    Optional. Specify a custom prefix for a given parameter. By default, Redis
    Sentinel configuration options are specified with the ``sentinel`` string,
    space as a separator needs to be included as well; some of the
    configuration options related to Redis daemon don't contain the prefix. If
    you need to add an option without the prefix, set this parameter to an
    empty string.

  ``separator``
    Optional, boolean. Add an empty line before a given option. This is
    a cosmetic parameter, which allows for better readability of the
    generated configuration file.

  ``multiple``
    Optional, boolean. If ``False``, and the parameter is not dynamic, and it's
    a list, the values will be concatenated into one string, separated by
    spaces. This is required by some of the Redis Server configuration options,
    for example ``bind``.

  If the ``name`` and ``value`` parameters are not present, each key of the
  YAML dictionary will be interpreted as a separate Redis Sentinel parameter.
  This can be used as a shorthand to define Redis Sentinel parameters, but for
  more complicated parameters (dynamic, with custom requirements), you should
  use the expanded form explained above.
