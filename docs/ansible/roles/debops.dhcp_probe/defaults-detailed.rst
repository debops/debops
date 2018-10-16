Default variable details
========================

Some of ``debops.dhcp_probe`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _dhcp_probe__ref_interfaces:

dhcp_probe__interfaces
----------------------

The ``dhcp_probe__*_interfaces`` variables contain a list of network interfaces
on which instances of :command:`dhcp_probe` will be listening for rogue DHCP
servers. The lists are merged together, users can modify contents of the
:envvar:`dhcp_probe__default_interfaces` by the entries in the
:envvar:`dhcp_probe__interfaces` variable.

Examples
~~~~~~~~

Enable DHCP Probe on custom interfaces:

.. code-block:: yaml

   dhcp_probe__interfaces:

     - name: 'br0'

     - name: 'br1'
       state: 'present'

Syntax
~~~~~~

Each list contains YAML dictionaries with specific parameters:

``name``
  Required. Name of the network interface (actually a :command:`systemd`
  instance) on which :command:`dhcp_probe` will be listening for rogue DHCP
  servers. This parameter is used as an anchor to merge multiple lists of
  interfaces together.

``state``
  Optional. If not specified or ``present`` the :command:`systemd` instance
  will be enabled. if ``absent``, the :command:`systemd` instance will be
  disabled.
