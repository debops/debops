.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.systemd`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _systemd__ref_configuration:

systemd__configuration
----------------------

The ``systemd__*_configuration`` default variables define the configuration of
the :command:`systemd` service itself. There are separate sets of variables for
the "system" instance, as well as a separate set of
``systemd__user_*_configuration`` variables for the global configuration of the
:command:`systemd --user` instances - both use the same configuration format.
You can find more details about :command:`systemd` configuration in the
:man:`systemd-system.conf(5)` manual page.

The ``systemd__logind_*_configuration`` variables define the configuration of
the :command:`systemd-logind` service. See :man:`loginf.conf(5)` for more
details about its configuration options.

The generated configuration will be located in the
:file:`/etc/systemd/{system,user,logind}.conf.d/ansible.conf` config files.
These files are not generated by default to fall back on the default
configuration provided in the OS packages; to generate them the
:envvar:`systemd__deploy_state` variable needs to be set to ``present``.

Examples
~~~~~~~~

You can check the :envvar:`systemd__default_configuration`,
:envvar:`systemd__user_default_configuration` and the
:envvar:`systemd__logind_default_configuration` variables for the default
contents of the configuration files.

Syntax
~~~~~~

The role uses the :ref:`universal_configuration` system to configure
:command:`systemd`. Each configuration entry in the list is a YAML dictionary.
The simple form of the configuration uses the dictionary keys as the parameter
names, and dictionary values as the parameter values. Remember that the
parameter names need to be specified in the exact case they are used in the
documentation (e.g.  ``LogLevel``, ``NUMAPolicy``), otherwise they will be
duplicated in the generated configuration file. It's best to use a single YAML
dictionary per configuration option.

If the YAML dictionary contains the ``name`` key, the configuration switches to
the complex definition mode, with configuration options defined by specific
parameters:

``name``
  Required. Specify the name of the :command:`systemd` configuration file
  parameter. The case is important and should be the same as specified in the
  configuration file or the :man:`systemd-system.conf(5)` manual page,
  otherwise the configuration entries will be duplicated.

  Multiple configuration entries with the same ``name`` parameter are merged
  together in order of appearance. This can be used to modify parameters
  conditionally.

``value``
  Required. The value of a given configuration option. It can be a string,
  number, ``True``/``False`` boolean or an empty string.

``state``
  Optional. If not specified or ``present``, a given configuration parameter
  will be present in the generated configuration file. If ``absent``, a given
  parameter will be removed from the configuration file. If ``comment``, the
  parameter will be present but commented out.

  If the state is ``init``, the parameter will be "primed" in the configuration
  pipeline, but it will be commented out in the generated configuration file.
  Any subsequent configuration entry with the same ``name`` will switch the
  state to ``present`` - this is used to define the default parameters in the
  role which can be changed via the Ansible inventory.

  If the state is ``ignore``, a given configuration entry will not be evaluated
  during role execution. This can be used to activate configuration entries
  conditionally.


.. _systemd__ref_units:

systemd__units
--------------

The ``systemd__*_units`` default variables can be used to manage
:command:`systemd` units (services, timers, etc.). The role supports management
of the system-wide units stored in the :file:`/etc/systemd/system/` directory,
as well as the :command:`systemd --user` instance units defined globally,
stored in the :file:`/etc/systemd/user/` directory (using
``systemd__user_*_units`` variables). You can find more information about the
units themselves in the :man:`systemd.unit(5)` manual page.

Examples
~~~~~~~~

Restart an existing service when the :ref:`debops.systemd` Ansible role is
applied on the host (without changing the configuration, this will be performed
on each role execution):

.. code-block:: yaml

   systemd__units:

     - name: 'systemd-sysctl.service'
       state: 'restarted'

Configure the network card on the system boot to permit Wake-On-LAN packets to
boot the host. The service will be created and executed on the next boot:

.. code-block:: yaml

   systemd__units:

     - name: 'wol.service'
       raw: |
         [Unit]
         Description=Configure Wake on LAN

         [Service]
         Type=oneshot
         ExecStart=/sbin/ethtool -s eth0 wol g

         [Install]
         WantedBy=basic.target
       state: 'present'

Create an example daemon which does nothing, ensure that it's started:

.. code-block:: yaml

   systemd__units:

     - name: 'sleeper.service'
       raw: |
         [Unit]
         Description=An example daemonized sleep command

         [Service]
         Type=simple
         ExecStart=/usr/bin/sleep 3600

         [Install]
         WantedBy=multi-user.target
       state: 'started'

Create an override for a specific service and change its description. Ensure
that the service is restarted when its configuration is changed:

.. code-block:: yaml

   systemd__units:

     - name: 'sleeper.service.d/description.conf'
       raw: |
         [Unit]
         Description=GSV Sleeper Service
       state: 'present'
       restart: 'sleeper.service'

Remove a specific unit override file without removing the whole service. The
service will be restarted to apply the changed configuration:

.. code-block:: yaml

   systemd__units:

     - name: 'sleeper.service.d/description.conf'
       state: 'absent'
       restart: 'sleeper.service'

Remove a service and all of its override files. The state of the service will
not be changed (running service stays running until the next host reboot):

.. code-block:: yaml

   systemd__units:

     - name: 'wol.service'
       state: 'absent'

     - name: 'sleeper.service'
       state: 'absent'

Syntax
~~~~~~

The role uses the :ref:`universal_configuration` system to manage
:command:`systemd` unit files. Each configuration entry in the list is a YAML
dictionary, with configuration options defined by specific parameters:

``name``
  Required. Name of the :command:`systemd` unit file to manage. The name can be
  in the form ``<unit.type>`` to denote a single :man:`systemd.unit(5)`, as
  well as ``<unit.type>.d/<override>.conf`` to denote a single "override"
  configuration file that changes the configuration of a specific unit.

  Unit files are stored either under the :file:`/etc/systemd/system/` or the
  :file:`/etc/systemd/user/` subdirectories, depending on the default variable
  used. The role will create the ``<unit.type>.d/`` subdirectories as needed.

  The ``name`` parameter needs to be unique. Multiple configuration entries
  with the same ``name`` parameter are merged together and override each other.

``raw``
  Optional. YAML text block in the INI format, with the :command:`systemd`
  configuration options which will be included in the generated configuration
  file as-is. The text block can contain Jinja statements to generate parts of
  the configuration dynamically.

  See the :man:`systemd.unit(5)` manual page for details about the unit
  configuration syntax and available options. The generated files are not
  validated by Ansible before being applied in the :command:`systemd`
  configuration at this time.

``state``
  Optional. If not specified or ``present`` (default), a given unit
  configuration file will be generated by Ansible and placed in the
  :command:`systemd` configuration directories. The role will ensure that the
  unit is enabled in :command:`systemd`, but the service will not be started by
  default.

  If ``started`` or ``stopped``, the configuration file will be generated and
  the unit will be enabled. The role will then try to ensure that the unit is
  in the desired state by starting or stopping it in :command:`systemd`.
  Specified actions will not be performed if a given configuration entry
  defines an unit override file.

  If ``restarted`` or ``reloaded``, the configuration file will be generated
  and the unit will be enabled. The role will tell :command:`systemd` to
  restart or reload the unit. This will be repeated on each execution of the
  role, unless the state parameter is updated. Specified actions will not be
  performed if a given configuration entry defines an unit override file.

  If ``absent``, the role will remove the specified unit configuration file as
  well as the override directory if it is present (all override files will be
  removed, even ones not managed by Ansible). Specific override files can be
  removed as well if they are defined directly in the ``name`` parameter.

  The role will not change the state of a running :command:`systemd` unit this
  way. Units will report their configuration as "not found" and will stay
  active until the next reboot or if they are stopped manually (Ansible
  currently cannot deal with such case properly via the
  ``ansible.builtin.systemd`` module).

  If ``init``, the configuration entry will be prepared, but no changes will be
  done on the host itself. This can be done to prepare a unit configuration and
  activate it conditionally later in the universal configuration pipeline.

  If ``ignore``, a given configuration entry will not be evaluated during role
  execution.

``restart``
  Optional. Specify the name of a :command:`systemd` unit (not the override).
  If a given entry generates a configuration file for a unit or its override
  with a "changed" state, or a given override is removed, the role will tell
  :command:`systemd` to restart a specified unit. This can be used to
  automatically restart services when their configuration is changed using unit
  override files. Because the template system in Ansible is idempotent,
  subsequent executions of the role should not restart the unit again when this
  parameter is used. This parameter is supported only for the system-wide unit
  configuration, not the "global" user configuration.

``comment``
  Optional. String or YAML text block with comments included in the generated
  configuration file.

``enabled``
  Optional, boolean. If ``True`` (default), the managed unit will be enabled in
  :command:`systemd` to be started on boot. If ``False``, the unit will not be
  started by default.

``masked``
  Optional, boolean. If ``True``, the role will tell :command:`systemd` to
  "mask" a unit to make it impossible to start, creating a symlink to
  :file:`/dev/null` file. If ``False``, a given unit will be "unmasked", so
  that it can be managed again.

``force``
  Optional, boolean. If ``True``, instruct the ``ansible.builtin.systemd``
  module to override existing symlinks.
