Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.libuser`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. contents::
   :local:
   :depth: 3


.. _libuser__ref_configuration:

libuser__configuration
----------------------

Examples
~~~~~~~~

See the :envvar:`libuser__original_configuration` variable for the original
contents of the :file:`/etc/libuser.conf` file and how they are represented in
the role configuration.

Syntax
~~~~~~

Each entry in the list is a YAML dictionary that describes the configuration file in the
:file:`/etc/libuser.conf`, using specific parameters:

``name``
  Required. This parameter defines the option name, and it needs to be unique
  in a given configuration file. Parameters from different options lists with
  the same ``name`` are merged together when the configuration entries are
  merged.

``options``
  Optional. A YAML list of :command:`libuser` configuration options defined in
  the configuration file. The ``options`` parameters from different
  configuration entries are merged together, therefore it's easy to modify
  specific parameters without the need to copy the entire value to the
  inventory.

  Each element of the options list is a YAML dictionary with specific
  parameters:

  ``name``
    Required for the main options. The Name of the libuser option to add.

  ``option``
    Optional. Override the ``name`` parameter to allow for multiple
    configuration options with the same parameter.

  ``state``
    Optional. If not specified or ``present``, the entry will be added in the
    configuration file. If ``absent``, the entry will be removed from the
    configuration file. If ``comment``, the entry will be included in the
    configuration file, but commented out.

  ``comment``
    Optional. String or a YAML text block with a comment added to a given
    configuration entry.

  ``separator``
    Optional, boolean. If ``True``, add an empty line before the configuration
    parameter, useful for visually separating configuration options.

  ``value``
    Optional for main options. If specified, set a value of a given option.
