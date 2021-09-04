.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.zabbix_agent`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _zabbix_agent__ref_configuration:

zabbix_agent__configuration
-----------------------

The ``zabbix_agent__*_configuration`` variables define the contents of the
:file:`/etc/zabbix_agent.conf` configuration file. The variables are combined in
order defined in the :envvar:`zabbix_agent__combined_configuration` variable and
can affect each other.

Examples
~~~~~~~~

Enable the Zabbix agent to allow all Zabbix servers on the 192.168.1.0/24 network:

.. code-block:: yaml

   zabbix_agent__configuration:
    - name: 'Server'
      value: '127.0.0.1,192.168.1.0/24'
      state: 'present'

You can see more examples in the :envvar:`default set of configuration options
defined by the role <zabbix_agent__default_configuration>`.

Syntax
~~~~~~

The configuration is defined as a list of YAML dictionaries, using
the :ref:`universal_configuration` format. The configuration entries can be
specified as simple "key: value" dictionaries, or if the ``name`` parameter is
used, can be defined using specific parameters:

``name``
  Required. The name of the configuration option.
  Multiple entries with the same ``name`` parameter are merged together in
  order of appearance and can affect each other.

``value``
  The value of a given configuration option. It can be a string, a number,
  or a boolean value - this is used to specify selected
  configuration options more than once. Empty strings are allowed.

``state``
  Optional. If not specified or ``present``, a given configuration option will
  be included in the generated config file. If ``absent``, a given
  configuration option will not be included in the file. If ``comment``, the
  option will be included, but commented out. If ``ignore``, a given
  configuration entry will not be processed during role execution.

``comment``
  Optional. A comment about a given configuration option.
