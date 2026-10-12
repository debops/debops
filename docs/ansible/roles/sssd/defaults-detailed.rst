.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2019-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.sssd`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.


.. _sssd__ref_configuration:

sssd__configuration
--------------------

The ``sssd__*_configuration`` variables define the contents of the
:file:`/etc/sssd/sssd.conf` configuration file. The variables are merged in
the order defined by the :envvar:`sssd__combined_configuration` variable, which
allows modification of the default configuration through the Ansible inventory.
See :man:`sssd.conf(5)` and the service-specific man pages (e.g.
:man:`sssd-ldap(5)`, :man:`sssd-krb5(5)` or :man:`sssd-sudo(5)`) for possible
configuration parameters and their values.

Examples
~~~~~~~~

See :envvar:`sssd__default_configuration` variable for an example of
existing configuration.

Enable debugging for the ``nss`` and ``pam`` subsystems:

.. code-block:: yaml

   sssd__configuration:

     - section: 'nss'
       options:
         - debug_level: '0x0770'

     - section: 'pam'
       options:
         - debug_level: '0x0770'


Enable enumeration (which means that ``sssd`` will download and cache all
users and groups from the LDAP server preemptively). This means that users
and groups will still be available in case of network outages, etc, but
enumeration is not suitable for large environments:

.. code-block:: yaml

   sssd__configuration:

     - section: 'domain/default'
       options:

         - name: 'enumerate'
           value: True


Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
the following parameters:

``section``
  Required. Name of the :man:`sssd.conf(5)` configuration section in which
  a given configuration option should be included. This parameter is used as an
  "anchor", configuration entries with the same ``section`` are combined
  together and affect each other in order of appearance.

``title``
  Optional. This parameter can be used to provide a short description
  of the section which will be included in the generated configuration file.

``state``
  Optional. If not specified or ``present``, a given section will be included
  in the generated configuration file. If ``absent``, the section will not be
  included in the file. If ``ignore``, a given configuration entry will not be
  evaluated during role execution. If ``hidden``, the section's header and title
  will be hidden in the generated configuration file.

``weight``
  Optional. A positive or negative number which selects the placement zone of
  a section in the generated configuration file: negative values move it to the
  top, ``0`` (the default) keeps it in the middle in source order, and positive
  values move it to the bottom. The magnitude of the value does not matter; use
  ``anchor_to`` for ordering relative to a specific section. See
  :ref:`universal_configuration_advanced_weight` for details.

``options``
  Required. A list of :command:`sssd` configuration options for a given
  section. The ``options`` parameters from configuration entries with the same
  ``section`` parameter are merged together in order of appearance and can
  affect each other.

  The options can be specified in a simple form as key/value pairs, where the
  key is the option name and value is the option value. Alternatively, if the
  ``name`` and ``value`` parameters are used, the entries can use an extended
  format with specific parameters:

  ``name``
    Required. The name of a given :man:`sssd.conf(5)` configuration option
    for a given ``section``. Options with the same ``section`` and ``name``
    will be merged in order of appearance.

  ``value``
    Required. The value of a given configuration option. It can be either
    a string, a boolean, a number, or a YAML list (elements will be joined with
    commas).

  ``raw``
    Optional. String or YAML text block which will be included in the
    configuration file "as is". If this parameter is specified, the ``name``
    and ``value`` parameters are ignored - you need to specify the
    entire line(s) with configuration option names as well.

  ``state``
    Optional. If not defined or ``present``, a given configuration option or
    section will be included in the generated configuration file. If ``absent``,
    ``ignore`` or ``init``, a given configuration option or section will not be
    included in the generated file. If ``comment``, the option will be included
    but commented out and inactive.

  ``comment``
    Optional. String or YAML text block that contains comments about a given
    configuration option.
