.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.lldpd`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _lldpd__ref_configuration:

lldpd__configuration
--------------------

These variables define the contents of the :file:`/etc/lldpd.d/`
configuration directory. Each configuration entry is a file with contents
defined either directly, or via the ``options`` parameter. You can read the
:man:`lldpcli(8)` manual page to see the available commands.

Examples
~~~~~~~~

The :envvar:`default role configuration <lldpd__default_configuration>`
includes creation of the ChassisID attribute override for virtual machines and
containers. To disable this functionality within the :command:`lldpd` daemon
itself, you can add an "unconfigure" command:

.. code-block:: yaml

   lldpd__configuration:

     - name: 'unchassis'
       options:
         - 'unconfigure system chassisid'

Alternatively, using the raw version:

.. code-block:: yaml

   lldpd__configuration:

     - name: 'unchassis'
       raw: |
         unconfigure system chassisid

Specify the device description attribute:

.. code-block:: yaml

   lldpd__configuration:

     - name: 'description'
       options:
         - 'configure system description': 'Custom device located in rack a1'

Syntax
~~~~~~

The variables are defined as lists of YAML dictionaries. Each dictionary
defines a separate configuration file in the :file:`/etc/lldpd.d/` directory.
Each configuration entry is defined using specific parameters:

``name``
  Required. Name of the generated configuration file, the role will include the
  :file:`.conf` suffix automatically. Configuration files are read by the
  daemon in alphabetical order so naming is important. Entries with the same
  ``name`` parameter can be overriden by subsequent entries.

``comment``
  Optional. String or YAML text block with additional comments included in
  a given configuration file.

``state``
  Optional. If not specified or ``present``, a given configuration file will be
  generated. If ``absent``, the configuration file will be removed from the
  host. If ``comment``, the configuration file will be generated but commands
  inside will be commented out. If ``ignore``, a given configuration entry will
  not be considered during template generation. This can be used to
  conditionally enable or disable configuration options.

``raw``
  String or YAML text block with :man:`lldpcli(8)` commands which will be
  included in the generated configuration file "as is".

``options``
  List of :man:`lldpcli(8)` commands which will be included in the generated
  configuration file. The ``options`` lists from multiple entries with the same
  ``name`` parameter are merged together. You can specify them either as
  a string which denotes the whole command, or as a YAML dictionary with key
  and value being the command and its argument quoted in double-quotes ("").
  Alternatively, you can define each command using a YAML dictionary with
  specific parameters:

  ``name``
    The :man:`lldpcli(8)` command. Multiple entris with the same ``name``
    parameter are merged together in order of appearance and can override each
    other.

  ``option``
    If a gien command needs to be specified multiple times with different
    values, you can use the ``option`` parameter to specify the actual
    :man:`lldpcli(8)` command to be included in the generated configuration
    file.

  ``value``
    The value of a given :man:`lldpcli(8)` command, surrounded by double
    quotes.

  ``state``
    If not defined or ``present``, a given command will be included in the
    generated configuration file. If ``absent``, a given command will not be
    included in the generated configuration file.
