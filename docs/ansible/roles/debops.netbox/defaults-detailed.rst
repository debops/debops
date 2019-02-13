Default variable details
========================

Some of ``debops.netbox`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

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
