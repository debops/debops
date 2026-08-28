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

.. _zabbix_agent__ref_scripts:

zabbix_agent__scripts
------------------------

List of helper scripts installed by the role in
:envvar:`zabbix_agent__scripts_path` (``/usr/local/lib/zabbix/`` by
default), usually referenced by commands in
:envvar:`zabbix_agent__user_parameters`. Each list item is a dictionary
with:

``name``
  Required. Filename of the script, relative to
  :envvar:`zabbix_agent__scripts_path`.

``src``
  Path to the script file relative to the role's or playbook project's
  ``files/`` directory, used as the ``ansible.builtin.copy`` module's
  ``src`` parameter.

``content``
  Alternative to ``src``, literal content of the script.

``mode``
  Optional. File mode of the installed script, ``'0755'`` by default.

``state``
  Optional. If not specified or ``present``, the script is installed. If
  ``absent``, the script is removed.

Example, installing a custom script and referencing it in a UserParameter:

.. code-block:: yaml

   zabbix_agent__host_scripts:

     - name: 'check-example.sh'
       src: 'files/zabbix/check-example.sh'
       mode: '0755'

   zabbix_agent__host_user_parameters:

     - key: 'example.check'
       command: '{{ zabbix_agent__scripts_path }}/check-example.sh'
       comment: 'Custom example check'

.. _zabbix_agent__ref_user_parameters:

zabbix_agent__user_parameters
--------------------------------

List of Zabbix Agent ``UserParameter`` entries rendered into
:envvar:`zabbix_agent__user_parameters_conf_path` (a drop-in file included
by the main agent configuration, separate from
:envvar:`zabbix_agent__configuration` to keep custom checks manageable on
their own). Each list item is a dictionary with:

``key``
  Required. The item key used to reference this check in Zabbix, for
  example ``example.check``.

``command``
  Required unless ``state`` is ``absent``. The shell command executed by
  the agent when the item is polled. Usually points at a script installed
  via :envvar:`zabbix_agent__scripts` in
  :envvar:`zabbix_agent__scripts_path`.

``unsafe``
  Optional, boolean. If ``True``, renders the entry as ``UserParameter``
  with the flexible/unsafe syntax accepting parameters
  (``key[*],command``) instead of a plain fixed key.

``comment``
  Optional. A comment rendered above the entry.

``state``
  Optional. If not specified or ``present``, the entry is included in the
  generated file. If ``absent``, it is skipped.

Example, defining a custom UserParameter directly without a separate
script:

.. code-block:: yaml

   zabbix_agent__host_user_parameters:

     - key: 'example.uptime_days'
       command: "awk '{print int($1/86400)}' /proc/uptime"
       comment: 'System uptime in days'

The role uses this mechanism internally to implement the built-in LXC
cgroup metrics, see :envvar:`zabbix_agent__cgroup_metrics`.
