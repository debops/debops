Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To configure volume snapshots on host given in
``debops_service_snapshot_snapper`` Ansible inventory group:

.. code:: ini

    [debops_service_snapshot_snapper]
    hostname

Example playbook
----------------

Here's an example playbook that can be used to manage cryptsetup::

   ---

   - name: Configure volume snapshots with snapper
     hosts: 'debops_service_snapshot_snapper'
     become: True

     roles:

       - role: debops.contrib-snapshot_snapper
         tags: [ 'role::snapshot_snapper' ]
