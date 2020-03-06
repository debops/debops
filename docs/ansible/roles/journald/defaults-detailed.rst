.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.journald`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _journald__ref_configuration:

journald__configuration
-----------------------

The ``journald__*_configuration`` default variables define the contents of the
:file:`/etc/systemd/journald.conf.d/ansible.conf` configuration file. This file
will be automatically parsed by the :command:`systemd-journald` service and any
active options will override the defaults defined in the
:file:`/etc/systemd/journald.conf` configuration file. You can read the
:man:`journald.conf(5)` manual page for more details about supported options.

Examples
~~~~~~~~

Configure disable persistent storage for the journal logs, using the simple
syntax:

.. code-block:: yaml

   journald__configuration:

     - 'Storage': 'volatile'

You can check the :envvar:`journald__default_configuration` variable for the
default contents of the configuration file.

Syntax
~~~~~~

Each configuration entry in the list is a YAML dictionary. The simple form of
the configuration uses the dictionary keys as the parameter names, and
dictionary values as the parameter values. Remember that the parameter names
need to be specified in the exact case they are used in the documentation (e.g.
``TTYPath``, ``ReadKMsg``), otherwise they will be duplicated in the generated
configuration file. It's best to use a single YAML dictionary per configuration
option.

If the YAML dictionary contains the ``name`` key, the configuration switches to
the complex definition mode, with configuration options defined by specific
parameters:

``name``
  Required. Specify the name of the Journal configuration file parameter. The
  case is important and should be the same as specified in the configuration
  file or the :man:`journald.conf(5)` manual page, otherwise the configuration
  entries will be duplicated.

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
