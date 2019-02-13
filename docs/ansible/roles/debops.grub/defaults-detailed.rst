Default variable details
========================

Some of ``debops.grub`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _grub__ref_configuration:

grub__configuration
-------------------

The ``grub__*_configuration`` variables define the contents of the
:file:`/etc/default/grub.d/ansible.cfg` configuration file. The variables are
lists of YAML dictionaries, the dictionaries with the same ``name`` parameter
are merged together in an order specified by the
:envvar:`grub__combined_configuration` variable, which allows some of the
configuration to be modified via Ansible inventory or other Ansible roles.


Examples
~~~~~~~~

Configure unattended filesystem check and repair on boot:

.. code-block:: yaml

   grub__configuration:
     - name: 'cmdline_linux_default'
       value:
         - 'fsck.mode=force'

Remove the ``quiet`` parameter from the default kernel command line:

.. code-block:: yaml

   grub__configuration:
     - name: 'cmdline_linux_default'
       value:
         - name: 'quiet'
           state: 'absent'


Syntax
~~~~~~

Each variable contains a list of YAML dictionaries, each dictionary defines
a configuration file option using specific parameters:

``name``
  Required. Name of a GRUB option, it's also used as an anchor for merging
  multiple configuration entries together.

  The option name should be specified as lowercase, without the ``GRUB_``
  prefix. For example:

  .. code-block:: none

     GRUB_DEFAULT       -> 'default'
     GRUB_CMDLINE_LINUX -> 'cmdline_linux'

  You can specify the full names with uppercase, but they will not be
  automatically merged with existing configuration.

``value``
  The value which should be set for a given GRUB option. Values can be YAML
  booleans, numbers, strings or lists of strings. Additionally, in a list you
  can specify values in an extended format as a YAML dictionary with
  parameters:

  ``name``
    The value you want to manage, a string.

  ``state``
    If not specified or ``present``, the value will be included in the
    configuration. If ``absent``, the value will be removed from the
    configuration. If ``ignore``, a given entry will not be evaluated by the
    role.

  The ``value`` parameters that contain YAML lists from multiple configuration
  entries are merged together.

``state``
  Optional. Specify the state of a given configuration entry. If not specified
  or ``present``, the entry will be set in the GRUB configuration file. If
  ``absent``, the entry will be removed from the configuration file. If
  ``ignore``, this configuration entry will not be evaluated by the role.

``comment``
  Optional. String or a YAML text block with a comment added to a given
  configuration option in the GRUB config file.

``quote``
  Optional, boolean. If not specified or ``True``, the value will be quoted. If
  ``False``, the value will not be quoted.

``original``
  Optional, boolean. If ``True``, the role will add ``$GRUB_<NAME>`` string to
  the given configuration option, based on the entry name. This allows to
  preserve existing GRUB options from the :file:`/etc/default/grub`; this is
  useful only for specific options like kernel parameters.

``export``
  Optional, boolean. if ``True``, the option will be exported in the GRUB
  environment by adding the ``export`` prefix in the configuration file. This
  is only needed in specific configuration scenarios.
