Default variable details
========================

Some of ``debops.haproxy`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _haproxy__ref_configuration:

haproxy__configuration
----------------------

The ``haproxy__*_configuration`` variables define the contents of the
:file:`/etc/haproxy/haproxy.cfg` configuration file. Each variable is a list of
YAML dictionaries. The list entries with the same ``name`` parameter are merged
together; this allows to change specific parameters in the Ansible inventory
without the need to copy over the entire variable contents.

Examples
~~~~~~~~

To see the examples of the configuration, you can look at the
:envvar:`haproxy__default_configuration` variable which defines the
:command:`haproxy` default configuration set by the role.

Syntax
~~~~~~

Each entry in the list is a YAML dictionary that describes the configuration file
in the :file:`/etc/haproxy/haproxy.cfg`, using specific parameters:

``name``
  Required. The filename of the generated configuration file, it should include
  a ``.cfg`` extension. This parameter is used to merge multiple entries with
  the same ``name`` together.

``options``
  Optional. A YAML list of :command:`haproxy` configuration options defined in
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

  ``state``
    Optional. If not specified or ``present``, a given option will be included
    in the configuration file. If ``absent``, an option will be removed from
    the configuration file. If ``comment``, an option will be included in the
    configuration file but commented out.

  ``value``
    Optional for main options. If specified, set a value of a given option.

  ``option``
    Required only when there are two or more lines with the same name, and
    the line have exactly 2 words:
    An example for this situation would be:

      option  httplog
      option  dontlognull

  .. code-block:: yaml

     haproxy__default_configuration:
       - name: 'defaults'
         options:

           - name: 'optionhttplog'
             option: 'option'
             value: 'httplog'
             state: 'present'

           - name: 'option'
             value: 'dontlognull'
             state: 'present'

  In this case, the ``name`` parameter is used as a handle, while the
  ``option`` parameter is used as the real name.
