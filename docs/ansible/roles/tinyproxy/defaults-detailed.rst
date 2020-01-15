Default variable details
========================

Some of ``debops.tinyproxy`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _tinyproxy__ref_configuration:

tinyproxy__configuration
------------------------

The ``tinyproxy__*_configuration`` variables define the contents of the
:file:`/etc/tinyproxy/tinyproxy.conf` configuration file. Each variable is a list of YAML
dictionaries. The list entries with the same ``name`` parameter are merged
together; this allows to change specific parameters in the Ansible inventory
without the need to copy over the entire variable contents.

Examples
~~~~~~~~

To see the examples of the configuration, you can look at the
:envvar:`tinyproxy__default_configuration` variable which defines the
:command:`tinyproxy` default configuration set by the role.

Syntax
~~~~~~

Each entry in the list is a YAML dictionary that describes the configuration file in the
:file:`/etc/tinyproxy/tinyproxy.conf`, using specific parameters:

``name``
  Required. The filename of the generated configuration file, it should include
  a ``.conf`` extension. This parameter is used to merge multiple entries with
  the same ``name`` together.

``options``
  Optional. A YAML list of :command:`tinyproxy` configuration options defined in
  the configuration file. The ``options`` parameters from different
  configuration entries are merged together, therefore it's easy to modify
  specific parameters without the need to copy the entire value to the
  inventory.

  Each element of the options list is a YAML dictionary with specific
  parameters:

  ``name``
    Required. This parameter defines the option name, and it needs to be unique
    in a given configuration file. Parameters from different options lists with
    the same ``name`` are merged together when the configuration entries are
    merged.

  ``comment``
    Optional. A string or YAML text block with a comment added to a given
    option.

  ``raw``
    Optional. Specify the raw :man:`tinyproxy(8)` configuration options as
    a string or a YAML text block. You can use this parameter to define
    :command:`tinyproxy` options that don't have specific values.

  ``state``
    Optional. If not specified or ``present``, a given option will be included
    in the configuration file. If ``absent``, an option will be removed from
    the configuration file. If ``comment``, an option will be included in the
    configuration file but commented out.
