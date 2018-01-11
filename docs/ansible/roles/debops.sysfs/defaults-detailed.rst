Default variable details
========================

Some of ``debops.sysfs`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _sysfs__ref_attributes:

sysfs__attributes
-----------------

The ``sysfs__*_attributes`` default variables hold the configuration of the
:command:`sysfsutils` service, stored in the :file:`/etc/sysfs.d/` directory.
The variables are lists, with each entry defined as a YAML dictionary.

Dictionaries can be specified as a simple attribute/value form where the
dictionary key is a path to a ``sysfs`` file, and the dictionary value is the
value to set, or can be defined as more complex YAML dictionaries with specific
parameters:

``name``
  Required. The name of the ``sysfs`` attribute to configure, usually specified
  as a filesystem path without the ``/sys/`` prefix.

  This parameter is used as the key when entries from multiple attribute lists
  are merged together. It's also used as a filename in the
  :file:`/etc/sysfs.d/` directory, with ``/`` characters replaced by ``_``,
  unless the ``item.filename`` parameter is used.

  If the ``item.options`` parameter is used, the ``sysfs`` attribute specified
  as the name is ignored and can be an arbitrary filename.

``value``
  Optional. Define the value of a given attribute. If ``item.options``
  parameter is used, the main ``value`` parameter is ignored.

``owner``
  Optional. Set the "owner" and "group" of a file in the :file:`/sys/`
  filesystem. Specify values supported by the :command:`chown` command. If the
  ``item.options`` parameter is used, the main ``owner`` parameter is ignored.

``mode``
  Optional. Set the file attributes of a file in the :file:`/sys/` filesystem.
  Specify values supported by the :command:`chmod` command. Make sure to quote
  the numerical values like ``0660``, otherwise they will be interpreted by
  Ansible as octal and may result in unexpected behaviour. If the
  ``item.options`` parameter is used, the main ``mode`` parameter is ignored.

``filename``
  Optional. A custom filename of the configuration file in
  :file:`/etc/sysfs.d/` directory. The ``.conf`` suffix is automatically
  appended.

``comment``
  Optional. A string or YAML text block with a comment included in the
  configuration file.

``state``
  Optional. Control the state of the generated configuration file.

  If not specified or ``present``, the configuration file will be generated.

  If ``absent``, an existing configuration file will be removed.

  If ``ignore``, a given entry is ignored by Ansible during configuration
  merge, this can be used to conditionally enable or disable configuration
  entries.

  If ``defined``, a given entry is defined during configuration merge, but it
  won't change the state of the configuration file on the managed hosts. This
  state is useful mostly in the role default variables to define ``sysfs``
  attributes which can be conditionally enabled from inventory or by other
  Ansible roles.

  If ``comment``, the configuration file will be generated, but all attributes
  will be commented out. This can be used to create example configuration
  files.

``options``
  Optional. YAML list of ``sysfs`` attributes with the same format as the one
  defined above. This parameter can be used to define multiple attributes in
  the same file. Supported parameters: ``name``, ``state``, ``value``,
  ``owner``, ``mode``, ``comment``.

Examples
~~~~~~~~

Define the example configuration from the :file:`/etc/sysfs.conf` as the role
configuration:

.. code-block:: yaml

   sysfs__attributes:

     - name: 'devices/system/cpu/cpu0/cpufreq/scaling_governor'
       comment: 'Always use the powersave CPU frequency governor'
       value: 'powersave'

     # Multiple attributes in one file
     - name: 'userspace_cpufreq_governor'
       comment: |
         Use userspace CPU frequency governor and set initial speed
       options:

         - name: 'devices/system/cpu/cpu0/cpufreq/scaling_governor'
           value: 'userspace'

         - name: 'devices/system/cpu/cpu0/cpufreq/scaling_setspeed'
           value: 600000

     - name: 'power/state'
       comment: 'Set permissions of suspend control file'
       mode: '0600'
       owner: 'root:power'
