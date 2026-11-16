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
---------------------------

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

Define a custom ``UserParameter`` check. The ``name`` parameter has to be
unique for each check, and the ``option`` parameter sets the actual name of
the configuration option:

.. code-block:: yaml

   zabbix_agent__configuration:

     - name: 'UserParameter_example_uptime_days'
       option: 'UserParameter'
       value: "example.uptime_days,awk '{print int($1/86400)}' /proc/uptime"
       comment: 'System uptime in days'

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

``option``
  Optional. Name of the configuration option, which will be used instead of the
  ``name`` parameter. This is useful when a Zabbix Agent option can be present
  multiple times in the configuration file.

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


.. _zabbix_agent__ref_api_lists:

Zabbix API lists
----------------

When :envvar:`zabbix_agent__api_register` is enabled, the host object in
Zabbix is configured from four groups of variables:

- host groups: :envvar:`zabbix_agent__api_default_host_groups`,
  :envvar:`zabbix_agent__api_host_groups`,
  :envvar:`zabbix_agent__api_group_host_groups` and
  :envvar:`zabbix_agent__api_host_host_groups`;

- linked templates: :envvar:`zabbix_agent__api_default_link_templates`,
  :envvar:`zabbix_agent__api_link_templates`,
  :envvar:`zabbix_agent__api_group_link_templates` and
  :envvar:`zabbix_agent__api_host_link_templates`;

- user macros: :envvar:`zabbix_agent__api_default_macros`,
  :envvar:`zabbix_agent__api_macros`,
  :envvar:`zabbix_agent__api_group_macros` and
  :envvar:`zabbix_agent__api_host_macros`;

- tags: :envvar:`zabbix_agent__api_default_tags`,
  :envvar:`zabbix_agent__api_tags`,
  :envvar:`zabbix_agent__api_group_tags` and
  :envvar:`zabbix_agent__api_host_tags`.

The lists in each group are combined in the order shown above, so the
entries from the inventory host override the entries from the inventory
groups, which override the ones defined for all hosts and the defaults of the
role.

Examples
~~~~~~~~

Link an additional template on the hosts in an inventory group and set
a macro used by that template:

.. code-block:: yaml

   zabbix_agent__api_group_link_templates:
     - 'Systemd by Zabbix agent 2'

   zabbix_agent__api_group_macros:
     - macro: '{$AGENT.TIMEOUT}'
       value: '10m'
       description: 'Wait 10 minutes before reporting that the agent is down'

Unlink the template on one of the hosts and change the value of the macro;
the description of the macro is kept from the group entry:

.. code-block:: yaml

   zabbix_agent__api_host_link_templates:
     - name: 'Systemd by Zabbix agent 2'
       state: 'absent'

   zabbix_agent__api_host_macros:
     - macro: '{$AGENT.TIMEOUT}'
       value: '1h'

Remove the host from a host group and remove a tag with a specific value:

.. code-block:: yaml

   zabbix_agent__api_host_host_groups:
     - name: 'Legacy servers'
       state: 'absent'

   zabbix_agent__api_host_tags:
     - tag: 'service'
       value: 'legacy'
       state: 'absent'

Syntax
~~~~~~

Host groups and templates are defined as lists of names, or YAML
dictionaries with specific parameters. Entries with the same ``name`` are
merged together in order of appearance:

``name``
  Required. The name of the host group, or the technical name of the template
  (the ``host`` field in the Zabbix API, which can differ from the visible name
  shown in the web interface).

``state``
  Optional. If not specified or ``present``, the host is added to the host
  group, or the template is linked to the host. Missing host groups are
  created automatically, missing templates are skipped with a warning.

  If ``absent``, the host is removed from the host group, or the template is
  unlinked from the host. Unlinked templates are not cleared, the items and
  other entities created from them are kept on the host and need to be removed
  in the Zabbix web interface if needed. Host groups in the ``absent`` state
  are not created.

  If ``init`` or ``ignore``, the entry is skipped; the host group or template
  is not added and not removed by the role.

User macros are defined as a list of YAML dictionaries. Entries with the same
``macro`` parameter are merged together in order of appearance, later entries
override the parameters of the earlier ones:

``macro``
  Required. The name of the macro, for example ``{$AGENT.TIMEOUT}``.

``value``
  The value of the macro.

``type``
  Optional. The type of the macro, as defined in the Zabbix API: ``0`` - text
  (default), ``1`` - secret text, ``2`` - vault secret.

``description``
  Optional. A description of the macro.

``state``
  Optional. If not specified or ``present``, the macro is configured on the
  host. If ``absent``, the macro is removed from the host, even if it was
  created outside of the role. If ``init`` or ``ignore``, the entry is
  skipped and a macro with this name created outside of the role is kept as
  it is.

Tags are defined as a list of YAML dictionaries. Zabbix allows the same tag
with different values, therefore tag entries are not merged; each entry is
a separate pair of a tag and its value:

``tag``
  Required. The name of the tag.

``value``
  Optional. The value of the tag, empty by default.

``state``
  Optional. If not specified or ``present``, the tag with this value is set on
  the host. If ``absent``, the tag with this value is removed from the host,
  including tags created outside of the role, and is not added by other
  entries. Tags with the same name and a different value are not affected.
  Entries in other states are skipped.

An entry without the ``state`` parameter keeps the state of an earlier entry
with the same ``name`` or ``macro``. For example, a template set to
``absent`` on the inventory group level stays absent when a host lists the
template again by its name; the host needs to set ``state: 'present'`` to link
it back.
