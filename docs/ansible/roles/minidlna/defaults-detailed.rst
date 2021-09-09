.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.minidlna`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _minidlna__ref_configuration:

minidlna__configuration
-----------------------

The ``minidlna__*_configuration`` variables define the contents of the
:file:`/etc/minidlna.conf` configuration file. The variables are combined in
order defined in the :envvar:`minidlna__combined_configuration` variable and
can affect each other.

Examples
~~~~~~~~

Define a set of media dirs to be scanned by MiniDLNA service:

.. code-block:: yaml

   minidlna__configuration:

     # Reset the default option to not include the '/var/lib/minidlna'
     # directory (optional)
     - media_dir: ''

     # Define a new set of media directories separated by type
     - name: 'media_dir'
       value:
         - 'A,/home/user/Music'
         - 'P,/home/user/Pictures'
         - 'V,/home/user/Videos'

You can see more examples in the :envvar:`default set of configuration options
defined by the role <minidlna__default_configuration>`.

Syntax
~~~~~~

The configuration is defined as a list of YAML dictionaries, using
the :ref:`universal_configuration` format. The configuration entries can be
specified as simple "key: value" dictionaries, or if the ``name`` parameter is
used, can be defined using specific parameters:

``name``
  Required. The name of the configuration option. See :man:`minidlna.conf(5)`
  to see more details about MiniDLNA configuration file and available options.
  Multiple entries with the same ``name`` parameter are merged together in
  order of appearance and can affect each other.

``value``
  The value of a given configuration option. It can be a string, a number,
  a boolean value or a YAML list of strings - this is used to specify selected
  configuration options more than once. Empty strings and lists are allowed.
  Lists in multiple configuration entries with the same ``name`` parameter are
  merged together; to "reset" a list, specify a configuration entry with an
  empty string.

``state``
  Optional. If not specified or ``present``, a given configuration option will
  be included in the generated config file. If ``absent``, a given
  configuration option will not be included in the file. If ``comment``, the
  option will be included, but commented out. If ``ignore``, a given
  configuration entry will not be processed during role execution.

``comment``
  Optional. A comment about a given configuration option.
