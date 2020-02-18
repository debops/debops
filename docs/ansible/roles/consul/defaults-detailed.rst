Default variable details
========================

Some of ``debops.consul`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _consul__ref_configuration:

consul__default_configuration
-----------------------------

The ``consul__*_configuration`` variables define the contents of the
:file:`/etc/consul.d/config.json` configuration file. Each variable is a list of YAML
dictionaries. The list entries with the same ``name`` parameter are merged
together; this allows to change specific parameters in the Ansible inventory
without the need to copy over the entire variable contents.

Examples
~~~~~~~~

To see the examples of the configuration, you can look at the
:envvar:`consul__default_configuration` variable which defines the
:command:`consul` default configuration set by the role.
