Default variable details
========================

Some of ``debops.varnish`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _varnish__ref_configuration:

varnish__configuration
----------------------

The ``varnish__*_configuration`` variables define the contents of the
:file:`/etc/varnish/default.vcl` configuration file. Each variable is a list of YAML
dictionaries. The list entries with the same ``name`` parameter are merged
together; this allows to change specific parameters in the Ansible inventory
without the need to copy over the entire variable contents.
