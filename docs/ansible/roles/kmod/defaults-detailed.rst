Default variable details
========================

Some of ``debops.kmod`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _kmod__ref_modules:

kmod__modules
-------------

The ``kmod__*_modules`` variables define what kernel module options should be
defined on the remote hosts, in the :file:`/etc/modprobe.d/` directory. Each
variable is a YAML list, each list entry is a YAML dictionary with specific
parameters:

``name``
  Required. Name of the kernel module to manage. This parameter is used as
  a marker to merge configuration entries of the same modules together.
  If the ``filename`` parameter is not specified, this parameter will be
  included in the generated filename, saved as ``{{ name }}.conf``.

``filename``
  Optional. Specify a custom filename for a given configuration snippet, the
  ``.conf`` extension needs to be included in the filename.

``state``
  Optional. Specify the state of the kernel module and its configuration.
  Multiple entries with the same ``name`` parameter are merged together in
  order of appearance; the ``state`` parameter can affect how the entries are
  merged.

  Supported states:

  ============= =============================================================
  Value         Description
  ============= =============================================================
  ``present``   **Default if not specified.** Configuration will be present
                and the role will try to unload and load the kernel module to
                apply any changes. Kernel module unloading is not forced, if
                the module cannot be unloaded, Ansible will error out.
  ------------- -------------------------------------------------------------
  ``absent``    The configuration of a given kernel module will be removed.
                If the configuration state changes, the role will try to
                unload the kernel module if it's loaded, in case of failure
                Ansible will error out.
  ------------- -------------------------------------------------------------
  ``config``    Specified kernel module configuration is set in the
                configuration file, but the role will not try to change the
                module state in the kernel.
  ------------- -------------------------------------------------------------
  ``blacklist`` The role will write the kernel module configuration and will
                try to unload the kernel module if it's currently loaded.
  ------------- -------------------------------------------------------------
  ``init``      Define initial configuration for a given kernel module, but
                don't write it in the configuration files or change the state
                of the kernel modules. Configuration defined with this state
                can be enabled conditionally using another list entry.
  ------------- -------------------------------------------------------------
  ``append``    Merge given configuration entry with other entries of the
                same name only if a given entry is supposed to be enabled
                (has a state other than ``init``). This state can be used to
                build configuration from multiple entries conditionally.
  ------------- -------------------------------------------------------------
  ``ignore``    Configuration entries with this state will not be evaluated
                by the role and won't be merged with other entries with the
                same ``name`` parameter.
  ============= =============================================================

``options``
  Optional. Specify the configuration options of the kernel module. This is
  a list of YAML dictionaries, each dictionary can have an option name as a key
  and an option value as a value. Alternatively, iv ``name`` and ``value`` keys
  are used, the dictionary can have the following parameters:

  =============== ===========================================================
  Key             Value
  =============== ===========================================================
  ``name``        Required. The option name.
  --------------- -----------------------------------------------------------
  ``value``       Required. The option value.
  --------------- -----------------------------------------------------------
  ``comment``     Optional. A custom comment added to a given option.
  --------------- -----------------------------------------------------------
  ``state``       Optional. If not set or ``present``, the option is included
                  in the configuration file, if ``absent``, the option is not
                  included in the configuration file.
  =============== ===========================================================

  The ``options`` parameters in multiple configuration entries are merged
  together, just like the main entries. This can be used to conditionally
  enable or disable options as needed.

``comment``
  Optional. String or YAML text block with a comment explaining the kernel
  module configuration.

``alias`` or ``aliases``
  Optional. String or a list of strings which specify aliases for a given
  module. See :man:`modprobe.d(5)` for more details.

``blacklist``
  Optional. String or a list of strings with kernel modules to blacklist. If
  this parameter is specified, the role does not try to unload individual
  modules; this can be useful to blacklist multiple modules at once
  preemptively.

``install``
  Optional. A shell command to execute by :command:`modprobe` command instead
  of loading a given kernel module. See :man:`modprobe.d(5)` for more details.

``remove``
  Optional. A shell command to execute by :program:`modprobe` command instead
  of unloading a given kernel module. See :man:`modprobe.d(5)` for more
  details.

``softdep``
  Optional. Define soft dependencies between kernel modules which affect the
  order of them being loaded into the kernel. See :man:`modprobe.d(5)` for more
  details. How to write the definition, based on an example from the manpage:

  .. code-block:: yaml

     kmod__modules:

       - name: 'c'
         softdep: 'pre: a b post: d e'

``raw``
  Optional. YAML text block which will be added at the end of the kernel module
  configuration file. It can be used to provide configuration not covered by
  other parameters.

Examples
~~~~~~~~

Disable PC Speaker support in the kernel:

.. code-block:: yaml

   kmod__modules:

     - name: 'pcspkr'
       state: 'blacklist'
       comment: 'Disable PC Speaker support'

On ThinkPad laptops, allow :command:`thinkfan` command to control the fan
speed:

.. code-block:: yaml

   kmod__modules:

     - name: 'thinkpad_acpi'
       comment: 'Enable fan speed control for "thinkfan"'
       options:
         - fan_control: 1


.. _kmod__ref_load:

kmod__load
----------

The ``kmod__*_load`` list variables can be used to specify which kernel modules
should be loaded at boot time. If a single module is specified, the role will
try to load it if it's currently not present in the kernel.

The configuration is stored in the :file:`/etc/modules-load.d/` directory on
hosts that use th :command:`systemd` service manager. On other hosts, the role
will modify the :file:`/etc/modules` file directly.

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the kernel module to manage. This parameter is used as
  a marker to merge configuration entries of the same modules together.
  If the ``filename`` parameter is not specified, this parameter will be
  included in the generated filename, saved as ``{{ name }}.conf``.

``filename``
  Optional. Specify a custom filename for a given configuration snippet, the
  ``.conf`` extension needs to be included in the filename.

``state``
  Optional. Specify the state of the kernel module and its configuration.
  Multiple entries with the same ``name`` parameter are merged together in
  order of appearance; the ``state`` parameter can affect how the entries are
  merged.

  Supported states:

  ============= =============================================================
  Value         Description
  ============= =============================================================
  ``present``   **Default if not specified.** Configuration will be present.
  ------------- -------------------------------------------------------------
  ``absent``    The configuration of a given kernel module will be removed.
  ------------- -------------------------------------------------------------
  ``config``    Specified kernel module configuration is set in the
                configuration file, but the role will not try to load the
                missing module into the kernel.
  ------------- -------------------------------------------------------------
  ``ignore``    Configuration entries with this state will not be evaluated
                by the role and won't be merged with other entries with the
                same ``name`` parameter.
  ============= =============================================================

``comment``
  Optional. String or YAML text block with a comment explaining the kernel
  module configuration.

``modules``
  Optional. List of modules to load on boot time. If specified, the string used
  in the ``name`` parameter is ignored. On non-:command:`systemd` hosts this
  parameter is ignored, use the ``name`` parameter instead.

Examples
~~~~~~~~

Load the ``pcspkr`` kernel module at boot time:

.. code-block:: yaml

   kmod__load:

     - name: 'pcspkr'
       comment: 'Enable PC Speaker support'
