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


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::snapshot_snapper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::snapshot_snapper:reinit``
  Execute tasks related to automatic reinitialization of volume snapshots.
