.. Copyright (C) 2017-2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017-2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.rabbitmq_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

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
   :lines: 1,5-


.. _rabbitmq_server__ref_config_options:

RabbitMQ configuration options
------------------------------

RabbitMQ is written in the `Erlang <https://en.wikipedia.org/wiki/Erlang_(programming_language)>`_
programming language, which is also used for its configuration. YAML, used by
Ansible, does not provide enough data types to directly map them to the
`Erlang data types <https://erlang.org/doc/reference_manual/data_types.html>`_
used in the RabbitMQ configuration file, therefore the configuration used by
``debops.rabbitmq_server`` focuses on description of the desired data types and
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

RabbitMQ configuration options are included in the ``options`` parameter of an
Erlang application section (see :ref:`rabbitmq_server__ref_config` for more
details). The ``options`` parameter is a YAML list, each entry is a YAML
dictionary. The dictionary keys are used as option names, and dictionary values
are used as option values. You can specify simple options this way:

.. literalinclude:: examples/simple-options.yml
   :language: yaml
   :lines: 1,5-

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
  is not specified, the template will try to select one based on the YAML value
  type. Supported value types:

  - ``string``: a quoted string, selected automatically if a YAML string is
    used as the value;

  - ``list``: a list of values, selected automatically if a YAML list is used
    as the value;

  - ``number``: an unquoted number, selected automatically if a YAML number or
    float is used as the value;

  - ``boolean``: a boolean ``true``/``false`` value, selected automatically if
    a YAML boolean is used as the value;

  - ``bit-string``: a `bit string <https://erlang.org/doc/reference_manual/data_types.html#bit-strings-and-binaries>`_
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
   :lines: 1,5-


.. _rabbitmq_server__ref_plugins:

rabbitmq_server__plugins
------------------------

The ``rabbitmq_server__*_plugins`` lists can be used to enable or disable
RabbitMQ plugins conditionally. You can find the available plugins on a given
host by running the command:

.. code-block:: console

   rabbitmq-plugins list

Each list entry is either a RabbitMQ plugin name, or a YAML dictionary with
specific parameters:

``name``
  The name of a RabbitMQ plugin to manage.

``state``
  Optional. If not defined or ``present``, the plugin will be enabled. If
  ``absent``, the plugin will be disabled.

``prefix``
  Optional. Custom install prefix to a Rabbit.

Examples
~~~~~~~~

Enable the RabbitMQ Management Console agent:

.. code-block:: yaml

   rabbitmq_server__plugins:

     - 'rabbitmq_management_agent'


.. _rabbitmq_server__ref_accounts:

rabbitmq_server__accounts
-------------------------

The ``rabbitmq_server__*_accounts`` list variables can be used to manage
RabbitMQ user accounts. Each list entry is a YAML dictionary with specific
parameters. The parameter names are the same as the ``rabbitmq_user`` Ansible
module. Some more common parameters:

``user`` or ``name``
  The name of a given user account.

``state``
  Optional. If not specified or ``present``, the user account will be created.
  If ``absent``, the user account will be removed.

``password``
  Optional. Plaintext password of a given user account. If not specified, the
  role will generate a random password and store it in the
  :file:`secret/rabbitmq_server/accounts/` directory on the Ansible Controller.
  See :ref:`debops.secret` Ansible role for more details.

``tags``
  Optional. A string or a YAML list of `tags <https://www.rabbitmq.com/management.html>`_
  assigned to a given account. Possible choices: ``management``,
  ``policymaker``, ``monitoring``, ``administrator``.

``vhost``
  Optional. Name of the virtual host to which a given set of permissions should
  apply. If not specified, ``/`` vhost is used by default.

``configure_priv``, ``read_priv``, ``write_priv``
  Optional. A regular expression which defines what resources on a given
  virtual host the user can configure, read from or write to. By default the
  ``^$`` regexp is used which means no permissions are given to any resources
  on a virtual host.

Examples
~~~~~~~~

Create an administrator account and a regular user account:

.. code-block:: yaml

   rabbitmq_server__accounts:

     - name: 'admin_account'
       vhost: '/'
       tags: [ 'administrator' ]
       configure_priv: '.*'
       read_priv: '.*'
       write_priv: '.*'

     - name: 'user_account'
       vhost: '/'
       read_priv: '.*'
       write_priv: '.*'


.. _rabbitmq_server__ref_user_limits:

rabbitmq_server__user_limits
-----------------------------

The ``rabbitmq_server__*_user_limits`` list variables can be used to configure
`RabbitMQ per-user connection limits`__ using Ansible. Each list entry is a YAML
dictionary with specific parameters. The parameter names are the same as the
``community.rabbitmq.rabbitmq_user_limits`` Ansible module.

.. __: https://www.rabbitmq.com/docs/user-limits

The available parameters:

``user``
  Required. Name of the RabbitMQ user to configure.

``node``
  Optional. Limit the user limits to a specific RabbitMQ node.

``max_connections``
  Optional. The maximum number of connections that can be open to a given
  RabbitMQ user.

``max_channels``
  Optional. The maximum number of channels that can be open to a given RabbitMQ
  user.

``state``
  Optional. If not specified or ``present``, the user limit will be created.
  If ``absent``, the user limit will be removed.

Examples
~~~~~~~~

Define limits for a specific user account:

.. code-block:: yaml

   rabbitmq_server__user_limits:

     - user: 'admin_account'
       max_connections: 1000
       max_channels: 100


.. _rabbitmq_server__ref_vhosts:

rabbitmq_server__vhosts
-----------------------

The ``rabbitmq_server__*_vhosts`` list variables can be used to manage
RabbitMQ virtual hosts. Each list entry is a YAML dictionary with specific
parameters. The parameter names are the same as the ``rabbitmq_vhost`` Ansible
module. Some more common parameters:

``name``
  The name of a given virtual host. If not specified, the whole list entry will
  be used as the name (see examples).

``state``
  Optional. If not specified or ``present``, the virtual host will be created.
  If ``absent``, the virtual host will be removed.

``tracing``
  Optional. Enable message tracing in a given virtual host.

Examples
~~~~~~~~

Create a set of virtual hosts:

.. code-block:: yaml

   rabbitmq_server__vhosts:

     - 'vhost1'

     - 'vhost2'

     - name: 'vhost3'
       state: 'absent'


.. _rabbitmq_server__ref_vhost_limits:

rabbitmq_server__vhost_limits
-----------------------------

The ``rabbitmq_server__*_vhost_limits`` list variables can be used to configure
`RabbitMQ virtual host limits`__ using Ansible. Each list entry is a YAML
dictionary with specific parameters. The parameter names are the same as the
``community.rabbitmq.rabbitmq_vhost_limits`` Ansible module. Available
parameters:

``vhost``
  Required. Name of the RabbitMQ virtual host to configure. The default virtual
  host is named ``/``.

``node``
  Optional. Limit the virtual host limits to a specific RabbitMQ node.

``max_connections``
  Optional. The maximum number of connections that can be open to a given
  RabbitMQ virtual host.

``max_queues``
  Optional. The maximum number of queues that can be created in a given RabbitMQ
  virtual host.

``state``
  Optional. If not specified or ``present``, the virtual host limit will be
  created. If ``absent``, the virtual host limit will be removed.

.. __: https://www.rabbitmq.com/docs/vhosts#limits

Examples
~~~~~~~~

Define virtual host limits for the default vhost:

.. code-block:: yaml

   rabbitmq_server__vhost_limits:

     - vhost: '/'
       max_connections: 1000
       max_queues: 100

Reset limists on the default vrrtual host:

.. code-block:: yaml

   rabbitmq_server__vhost_limits:

     - vhost: '/'
       state: 'absent'


.. _rabbitmq_server__ref_exchanges:

rabbitmq_server__exchanges
--------------------------

The ``rabbitmq_server__*_exchanges`` list variables can be used to manage
`RabbitMQ exchanges`__. Each list entry is a YAML dictionary with specific
parameters. The parameter names are the same as the
``community.rabbitmq.rabbitmq_exchange`` Ansible module.

.. __: https://www.rabbitmq.com/tutorials/amqp-concepts.html#exchanges

List of supported parameters:

``name``
  Required. The name of a given RabbitMQ exchange.

``vhost``
  Optional. Specify the RabbitMQ virtual host to which a given exchange applies.

``exchange_type``
  Optional. The type of a given RabbitMQ exchange. Supported choices:
  ``direct``, ``fanout``, ``topic``, ``headers``, ``x-consistent-hash``,
  ``x-delayed-message``, ``x-random``, ``x-recent-history``.

``durable``
  Optional. If not specified or ``True``, the exchange will be durable. If
  ``False``, the exchange will be transient.

``auto_delete``
  Optional. If not specified or ``False``, the exchange will not be deleted
  when the last queue is unbound from it. If ``True``, the exchange will be
  deleted when the last queue is unbound from it.

``internal``
  Optional. If not specified or ``False``, the exchange will be a regular
  exchange. If ``True``, the exchange will be an internal exchange, only
  available for other exchanges.

``arguments``
  Optional. A YAML dictionary with additional arguments to set for a given
  exchange.

``state``
  Optional. If not specified or ``present``, the exchange will be created. If
  ``absent``, the exchange will be removed.

Examples
~~~~~~~~

Create a set of RabbitMQ exchanges:

.. code-block:: yaml

   rabbitmq_server__exchanges:

     - name: 'exchange1'
       exchange_type: 'fanout'
       durable: False
       auto_delete: True

     - name: 'exchange2'
       exchange_type: 'topic'
       durable: True
       auto_delete: False


.. _rabbitmq_server__ref_queues:

rabbitmq_server__queues
-----------------------

The ``rabbitmq_server__*_queues`` list variables can be used to manage `RabbitMQ
queues`__. Each list entry is a YAML dictionary with specific parameters. The
parameter names are the same as the ``community.rabbitmq.rabbitmq_queue``
Ansible module.

.. __: https://www.rabbitmq.com/tutorials/amqp-concepts.html#queues

List of supported parameters:

``name``
  Required. The name of a given RabbitMQ queue.

``vhost``
  Optional. Specify the RabbitMQ virtual host to which a given queue applies.

``durable``
  Optional. If not specified or ``True``, the queue will be durable. If
  ``False``, the queue will be transient.

``auto_delete``
  Optional. If not specified or ``False``, the queue will not be deleted when
  the last consumer is removed. If ``True``, the queue will be deleted when the
  last consumer is removed.

``auto_expires``
  Optional. The time in milliseconds after which the queue will be deleted if
  it is not used.

``dead_letter_exchange``
  Optional. The name of a dead-letter exchange to which messages will be
  republished if they are rejected or expire.

``dead_letter_routing_key``
  Optional. The routing key to use when republishing messages to the dead-letter
  exchange.

``max_length``
  Optional. The maximum number of messages that the queue will hold.

``max_priority``
  Optional. The maximum priority of messages that the queue will hold.

``message_ttl``
  Optional. The time in milliseconds after which a message will be removed from
  the queue if it is not consumed.

``arguments``
  Optional. A YAML dictionary with additional arguments to set for a given
  queue.

``state``
  Optional. If not specified or ``present``, the queue will be created. If
  ``absent``, the queue will be removed.

Examples
~~~~~~~~

Create a set of RabbitMQ queues:

.. code-block:: yaml

   rabbitmq_server__queues:

     - name: 'queue1'
       durable: False
       auto_delete: True
       state: 'present'

     - name: 'queue2'
       durable: True
       auto_delete: False
       state: 'present'


.. _rabbitmq_server__ref_bindings:

rabbitmq_server__bindings
-------------------------

The ``rabbitmq_server__*_bindings`` list variables can be used to manage
`RabbitMQ bindings`__. Each list entry is a YAML dictionary with specific
parameters. The parameter names are the same as the
``community.rabbitmq.rabbitmq_binding`` Ansible module.

.. __: https://www.rabbitmq.com/tutorials/amqp-concepts.html#bindings

List of parameters:

``name``
  Required. The name of a given RabbitMQ exchange which will be the source of a
  given binding.

``destination``
  Required. The name of a given RabbitMQ queue or another exchange which will be
  a destination of a given binding.

``destination_type``
  Required. The type of a given destination. Supported choices: ``queue``,
  ``exchange``.

``vhost``
  Optional. Specify the RabbitMQ virtual host to which a given binding applies.

``routing_key``
  Optional. The routing key to use when binding a queue to an exchange.

``arguments``
  Optional. A YAML dictionary with additional arguments to set for a given
  binding.

``state``
  Optional. If not specified or ``present``, the binding will be created. If
  ``absent``, the binding will be removed.

Examples
~~~~~~~~

Create a set of RabbitMQ bindings:

.. code-block:: yaml

   rabbitmq_server__bindings:

     - name: 'exchange1'
       destination: 'queue1'
       destination_type: 'queue'
       routing_key: 'example'
       state: 'present'

     - name: 'exchange2'
       destination: 'exchange1'
       destination_type: 'exchange'
       state: 'present'


.. _rabbitmq_server__ref_feature_flags:

rabbitmq_server__feature_flags
------------------------------

The ``rabbitmq_server__*_feature_flags`` list variables can be used to manage
`RabbitMQ feature flags`__. Each list entry is a YAML dictionary with specific
parameters. The parameter names are the same as the
``community.rabbitmq.rabbitmq_feature_flag`` Ansible module.

.. __: https://www.rabbitmq.com/feature-flags.html

Supported parameters:

``name``
  Required. The name of a given RabbitMQ feature flag.

``node``
  Optional. The name of a RabbitMQ node to which a given feature flag applies.

Examples
~~~~~~~~

Enable the ``maintenance_mode_status`` feature flag on a specific Erlang node:

.. code-block:: yaml

   rabbitmq_server__feature_flags:

     - name: 'maintenance_mode_status'
       node: 'rabbit@node1'


.. _rabbitmq_server__ref_global_parameters:

rabbitmq_server__global_parameters
----------------------------------

The ``rabbitmq_server__*_global_parameters`` list variables can be used to
manage `RabbitMQ global parameters`__, defined for the entire cluster. Each list
entry is a YAML dictionary with specific global parameters. The parameter names
are the same as the ``community.rabbitmq.rabbitmq_global_parameter`` Ansible
module.

.. __: https://www.rabbitmq.com/docs/parameters#parameter-management

Configuration entry parameters:

``name``
  Required. The name of a given RabbitMQ parameter being set.

``value``
  The value of a given parameter in a JSON format. The values are usually
  quoted using single quotes and contain double-quotes.

``node``
  Optional. The name of a RabbitMQ node to which a given parameter applies.

``state``
  Optional. If not specified or ``present``, the parameter will be created.
  If ``absent``, the parameter will be removed.

Examples
~~~~~~~~

Set the value of the ``cluster_name`` global parameter:

.. code-block:: yaml

   rabbitmq_server__global_parameters:

     - name: 'cluster_name'
       value: '"my-cluster"'
       state: 'present'


.. _rabbitmq_server__ref_parameters:

rabbitmq_server__parameters
---------------------------

The ``rabbitmq_server__*_parameters`` list variables can be used to manage
`RabbitMQ parameters <https://www.rabbitmq.com/parameters.html>`_. Each list
entry is a YAML dictionary with specific parameters. The parameter names are
the same as the ``rabbitmq_parameter`` Ansible module. Some more common
parameters:

``component``
  Required. Name of the component of which the parameter is being set.

``name``
  Required. The name of a given RabbitMQ parameter being set.

``value``
  The value of a given parameter in a JSON format. The values are usually
  quoted using single quotes and contain double-quotes.

``vhost``
  Optional. Specify the RabbitMQ virtual host to which a given parameter
  applies.

``state``
  Optional. If not specified or ``present``, the parameter will be created.
  If ``absent``, the parameter will be removed.

Examples
~~~~~~~~

Define a RabbitMQ parameter:

.. code-block:: yaml

   rabbitmq_server__parameters:

     - component: 'federation'
       name: 'local-username'
       value: '"guest"'


.. _rabbitmq_server__ref_policies:

rabbitmq_server__policies
-------------------------

The ``rabbitmq_server__*_policies`` list variables can be used to manage
`RabbitMQ policies <https://www.rabbitmq.com/parameters.html>`_. Each list
entry is a YAML dictionary with specific parameters. The parameter names are
the same as the ``rabbitmq_policy`` Ansible module. Some more common
parameters:

``name``
  Required. The name of a given RabbitMQ policy.

``pattern``
  Required. A regexp pattern of RabbitMQ queue names to which a given policy applies.

``tags``
  Required. An YAML dictionary with key/value parameters that describe the
  policy. Relevant documentation can be found in the RabbitMQ Management
  Console, Admin section, Policies.

``vhost``
  Optional. Specify the RabbitMQ virtual host to which a given policy applies.

``apply_to``
  Optional. The resource type to which a given policy applies to. Supported
  choices: ``all``, ``exchanges``, ``queues``. If not specified, ``all`` is
  used by default.

``state``
  Optional. If not specified or ``present``, the policy will be created.
  If ``absent``, the policy will be removed.

``priority``
  Optional. The numerical priority of a given policy, used for sorting.

Examples
~~~~~~~~

Create a set of RabbitMQ policies:

.. code-block:: yaml

   rabbitmq_server__policies:

     - name: 'HA'
       pattern: '.*'
       tags:
         'ha-mode': 'all'
