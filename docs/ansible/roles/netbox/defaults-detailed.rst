.. Copyright (C) 2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.netbox`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _netbox__ref_virtualenv_pip_packages:

netbox__virtualenv_pip_packages
-------------------------------

This is a list of additional Python modules that will be installed in the
NetBox ``virtualenv`` environment using ``pip``. Each element is either
a string which specifies a Python module name, or a YAML dictionary with
specific parameters:

``name``
  Name of the Python module to install.

``version``
  Optional. Specific version of the module to install.

``state``
  Optional. If not specified or ``present``, the Python module will be
  installed. If ``ignore``, the specified Python module will be ignored.

The Python modules will be installed or updated as needed when the NetBox
checked out code is updated.

.. _netbox__config_plugins_config:

netbox__config_plugins_config
-----------------------------

YAML dictionary where the key is the plugin name. The value can be any nested
data structure. What is supported as value is defined by the individual plugin.

Example:

.. code-block:: yaml

   netbox__config_plugins_config:
     netbox_topology_views:
       preselected_device_roles:
         - 'Access point'
         - 'Firewall'
         - 'Peripheral'
         - 'Power'
         - 'Server'
         - 'Switch'
