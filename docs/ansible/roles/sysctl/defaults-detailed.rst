Default variable details
========================

Some of ``debops.sysctl`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _sysctl__ref_writable:

sysctl__writable
----------------

Certain parts of the :man:`proc(5)` filesystem can be mounted with read-only
permissions to limit privileges in certain contexts, like unprivileged
containers. Usually the :file:`/proc/sys/` filesystem is bind-mounted as
read-only and specific paths inside which are correctly namespaced by the
kernel, for example :file:`/proc/sys/net/` directory, are bind-mounted with
read-write permissions.

When the :program:`sysctl` command tries to modify kernel parameters in
read-only path, it returns with an error. Since the ``debops.sysctl`` calls the
:program:`sysctl` command directly, in such case the playbook execution will
stop and users will be forced to manually recover from the error.

To avoid this, the role checks via Ansible local facts, what paths in
:file:`/proc/sys/` directory are writable, and only creates configuration
entries for the paths that can be modified in the current context. Any
parameters that cannot modify kernel variables will be automatically commented
out with additional comment marking that parameter as read-only.

This mechanism is controlled by the :envvar:`sysctl__writable` default
variable. It contains a list of paths in the :file:`/proc/sys/` directory which
can be written to, for example:

.. code-block:: yaml

   sysctl__writable: [ 'net', 'fs.nfs', 'kernel' ]

The path elements need to be separated by a dot (``.``) instead of a slash
(``/``) to be correctly used by the role.


.. _sysctl__ref_parameters:

sysctl__parameters
------------------

The ``sysctl__*_parameters`` variables contain configuration of the kernel
parameters stored in the :file:`/etc/sysctl.d/` directory. The variables are
merged in the order specified by the :envvar:`sysctl__combined_parameters`
variable, the parameters can be manipulated using Ansible inventory without the
need to copy the entire default variable.

Each list entry is a YAML dictionary that defines one configuration file with
specific parameters:

``name``
  Required. Name of the configuration section. Multiple entries with the same
  name will be merged together in order of appearance. The name is used as
  a part of the filename and it's best not to change it without complete
  redeployment of the configuration file.

``filename``
  Optional. Specify the filename of the configuration file to manage in the
  :file:`/etc/sysctl.d/` directory (the ``.conf`` suffix needs to be included).
  If the ``filename`` parameter is not specified, the file will be named as:

  .. code-block:: none

     /etc/sysctl.d/{{ weight }}-{{ name }}.conf

``divert``
  Boolean, optional. When specified and ``True``, the original configuration
  file will be diverted using :man:`dpkg-divert(8)`. If a configuration file is
  due to be removed, the original file will be reverted back into place.

``comment``
  Optional. A string or YAML text block with a comment added at the top of the
  generated configuration file.

``state``
  Optional. Specify the desired state of the configuration file. Known states:

  ============= =============================================================
  Value         Description
  ============= =============================================================
  ``present``   **Default if not specified.** The configuration file will be
                generated in the :file:`/etc/sysctl.d/` directory.
  ------------- -------------------------------------------------------------
  ``absent``    The configuration file will be removed from the
                :file:`/etc/sysctl.d/` directory if present, and it won't be
                generated.
  ------------- -------------------------------------------------------------
  ``comment``   The configuration file will be generated but all of the
                kernel parameters will be commented out. This can be used to
                disable the entire configuration file, preserving the set
                parameter values for reference.
  ------------- -------------------------------------------------------------
  ``ignore``    A given configuration entry will not be processed by the role
                and all of the kernel parameters defined in it will not be
                present in the generated configuration file.
  ============= =============================================================

``options``
  Required. A list of entries that define kernel parameters present in a given
  configuration file. Each entry is a YAML dictionary, the entries can be
  specified in a simple or complex form. An example of a simple form:

  .. code-block:: yaml

     sysctl__parameters:
       - name: 'network'
         options:

           - 'net.ipv4.ip_forward': True

           - 'net.ipv4.icmp_ratelimit': 100

  Complex form is enabled when the ``name`` parameter is used. You can use the
  parameters:

  ``name``
    Required. Name of the kernel parameter to configure.

  ``value``
    Required. The value of a given kernel parameter which should be set. Values
    can be YAML booleans (converted to ``0`` or ``1`` in the configuration
    file), numbers and strings.

  ``comment``
    Optional. String or YAML text block with additional comments about a given
    kernel parameter.

  ``state``
    Optional. Specify the desired state of a given kernel parameter. Possible
    states:

    ============= ===========================================================
    Value         Description
    ============= ===========================================================
    ``present``   The kernel parameter will be present in the generated
                  configuration file.
    ------------- -----------------------------------------------------------
    ``absent``    The kernel parameter will be absent from the configuration
                  file.
    ------------- -----------------------------------------------------------
    ``comment``   The kernel parameter will be present in the configuration
                  file, but it will be commented out.
    ------------- -----------------------------------------------------------
    ``ignore``    A given option will be ignored by the role during template
                  generation.
    ============= ===========================================================

  The ``options`` parameters from multiple configuration entries with the same
  ``name`` parameter are merged, you can use this to modify existing parameters
  defined in the role default variables via Ansible inventory, without copying
  the entire default variable.

Examples
~~~~~~~~

Enable IPv4 forwarding using the default configuration:

.. code-block:: yaml

   sysctl__parameters:

     - name: 'network'
       options:

         - name: 'net.ipv4.ip_forward'
           Value: True

You can also check the :envvar:`sysctl__default_parameters` variable for more
examples.
