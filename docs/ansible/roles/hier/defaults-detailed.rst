.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _hier__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.hier`` default variables have more extensive configuration than
simple strings or lists, here you can find documentation and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _hier__ref_directories:

hier__directories
-----------------

The ``hier__*_directories`` variables define the list of base directories to
create by the role. The directory paths are saved using an Ansible local fact
to ensure that any changes after applying the role don't affect an existing
installation. To modify existing paths, the
:file:`/etc/ansible/facts.d/hier.fact` script should be removed from the host,
this will ensure that the role does not use existing paths from the facts.

Examples
~~~~~~~~

Modify the application data directory to store them in a separate mount point
instead of the :file:`/srv/` directory (you can use :ref:`debops.mount` role to
mount a local device under that directory, or :ref:`debops.nfs` to configure
a remote NFS filesystem):

.. code-block:: yaml

   hier__directories:

     - name: 'data'
       path: '/data'

Remember that this change will only take effect on first application of the
role, therefore it should be defined in the Ansible inventory before the host
is provisioned.

Syntax
~~~~~~

Each base directory is defined as a YAML dictionary with specific parameters:

``name``
  Required. The short name of the directory, used as a reference in the Ansible
  local facts. The configuration entries with the same ``name`` parameter are
  merged together, this can be used to modify the paths defined by the role via
  Ansible inventory.

``path``
  Required. An absolute path of the base directory to create. The path needs to
  start with the ``/`` character, otherwise it will not be created by the role.

``state``
  Optional. If not specified or ``present``, the path will be created by the
  role. If ``absent``, the role will not create this path (existing paths are
  not removed).
