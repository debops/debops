Default variable details
========================

Some of the ``debops.rabbitmq_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _rabbitmq_server__ref_config:

rabbitmq_server__config
-----------------------

The ``rabbitmq_server__*_config`` variables describe contents of the
:file:`/etc/rabbitmq/rabbitmq.config` configuration file. Each entry in the
``rabbitmq_server__*_config`` variables is a YAML dictionary with specific
parameters:

``name``
  Required. The name of an Erlang application to configure. Each application
  can contain a set of configuration options. Configuration options from
  multiple applications with the same ``name`` parameter are merged together.

``state``
  Optional. If not specified or ``present``, a given application configuration
  will be included in the finished configuration file.

  If ``absent``, a given application configuration will be removed from the
  configuration file.

  If ``ignore``, a given application entry is not evaluated by the
  configuration template. This can be used to conditionally enable or disable
  configuration sections.

``comment``
  Optional. A string or YAML text block which will be added as a comment to the
  configuration section.

``weight``
  Optional. A positive or negative number which will be used to affect the
  position of a given Erlang application within the configuration file. The
  higher the number, the more a given application section "weighs", and
  therefore it will be placed lower in the finished configuration file.
  If not specified, ``0`` is used by default.

``options``
  A YAML list of configuration options for a given Erlang application.
  See :ref:`rabbitmq_server__ref_config_options` for more details.

Examples
~~~~~~~~

.. literalinclude:: examples/example-config-sections.yml
   :language: yaml


.. _rabbitmq_server__ref_config_options:

RabbitMQ configuration options
------------------------------

RabbitMQ is written in the `Erlang <https://en.wikipedia.org/wiki/Erlang_(programming_language)>`_
programming language, which is also used for its configuration. YAML, used by
Ansible, does not provide enough data types to directly map them to the
`Erlang data types <http://erlang.org/doc/reference_manual/data_types.html>`_
used in the RabbitMQ configuration file, therefore the configuration used by
debops.rabbitmq_ focuses on description of the desired data types and
conditional activation of the configuration sections. This means that simple
values like strings, numbers, lists are mapped directly, however more complex
configuration needs to be written in Erlang using YAML text blocks. The role
tries to detect the value type automatically, but in some cases you might need
to use the extended YAML dictionary syntax described below.

The role does not provide original configuration variables due to the issues
with template generation (commented out options are not supported). You can
find a reference RabbitMQ configuration file after the service installation, in
the :file:`/usr/share/doc/rabbitmq-server/rabbitmq.config.example.gz` file.
An `example rabbitmq.config file <https://github.com/rabbitmq/rabbitmq-server/blob/master/docs/rabbitmq.config.example>`_
is also available online.

RabbitMQ configuration options are included in the ``options`` paramter of an
Erlang application section (see :ref:`rabbitmq_server__ref_config` for more
details). The ``options`` parameter is a YAML list, each entry is a YAML
dictionary. The dictionary keys are used as option names, and dictionary values
are used as option values. You can specify simple options this way:

.. literalinclude:: examples/simple-options.yml
   :language: yaml

If a given dictionary contains a ``name`` parameter, the configuration template
will switch to a more verbose option interpretation, using known parameters:

``name``
  The name of a given configuration option. Multiple entries with the same name
  are merged together, with the latter ones takim precedence over the former.

``value``
  Required. A value to set for a given option. The value can be an YAML string,
  a list, number, boolean.

  YAML text block is used to indicate a raw Erlang code which should be used as
  a value. The raw Erlang code should not end with any flow control Erlang
  characters (``}`` or ``},``), they will be added automatically by the role.

``type``
  Optional. Specify the type of a given value to use. If the ``type`` parameter
  is not specifed, the template will try to select one based on the YAML value
  type. Supported value types:

  - ``string``: a quoted string, selected automatically if a YAML string is
    used as the value;

  - ``list``: a list of values, selected automatically if a YAML list is used
    as the value;

  - ``number``: an unquoted number, selected automatically if a YAML number or
    float is used as the value;

  - ``boolean``: a boolean ``true``/``false`` value, selected automatically if
    a YAML boolean is used as the value;

  - ``bit-string``: a `bit string <http://erlang.org/doc/reference_manual/data_types.html#id70212>`_
    value with special quotation marks. Only YAML strings are supported at this
    time;

  - ``bit-list``: a list of bit-strings with special quotation marks. Only YAML
    strings are supported at this time. if the value type is set as
    ``bit-string`` and a YAML list is set, the role should change to
    a ``bit-list`` type automatically;

  - ``raw``: a raw Erlang expression, inserted in the finished configuration
    file as-is. The Erlang code should not end with Erlang flow control
    characters ``}`` or ``},``, they will be added automatically by the role.
    if the value is specified using a YAML text block, the ``raw`` type should
    be selected automatically, based on the number of lines used in the value;

``option``
  Optional. If specified, the configuration option will use this value for the
  name instead of ``name``.

``state``
  Optional. If not specified or ``present``, a given option be included in the
  finished configuration file.

  If ``absent``, a given option will be removed from the configuration file.

  If ``ignore``, a given option entry is not evaluated by the configuration
  template. This can be used to conditionally enable or disable configuration
  options.

``comment``
  Optional. A string or YAML text block which will be added as a comment to the
  configuration option.

``weight``
  Optional. A positive or negative number which will be used to affect the
  position of a given option within the configuration file. The higher the
  number, the more a given option "weighs", and therefore it will be placed
  lower in the finished configuration file. If not specified, ``0`` is used by
  default.

Examples
~~~~~~~~

.. literalinclude:: examples/verbose-options.yml
   :language: yaml
