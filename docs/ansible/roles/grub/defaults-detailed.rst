.. Copyright (C) 2015 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2015-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.grub`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

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

The ``quiet`` parameter for the default kernel command line is usually defined
in :file:`/etc/default/grub` and imported into
:file:`/etc/default/grub.d/ansible.cfg` via the ``original`` parameter (see
below). If you want to remove the ``quiet`` default parameter, you therefore
need to *not* import the original value(s):

.. code-block:: yaml

   grub__configuration:
     - name: 'cmdline_linux_default'
       original: False

If you do so, make sure that you're not unintentionally excluding any other
parameters already set in :file:`/etc/default/grub`.


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
  Optional, boolean. If ``True``, the role will add a ``$GRUB_<NAME>`` string
  to the given configuration option, based on the entry name. This allows
  existing GRUB options from the :file:`/etc/default/grub` to be preserved
  and is generally only useful for specific options like kernel parameters.

``export``
  Optional, boolean. if ``True``, the option will be exported in the GRUB
  environment by adding the ``export`` prefix in the configuration file. This
  is only needed in specific configuration scenarios.
