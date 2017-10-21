Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To configure iSCSI Targets on a particular host, you need to add it to the
``[debops_tgt]`` host group in Ansible inventory::

    [debops_tgt]
    hostname

By default no targets are configured. You should create either files, disk
partitions or LVM volumes and then configure them using ``tgt_targets`` list
variable. See :ref:`tgt_targets` for more details.

Example playbook
----------------

Here's an example playbook which uses ``debops.tgt`` role::

    ---

    - name: Configure iSCSI Target service
      hosts: debops_tgt

      roles:
        - role: debops.tgt
          tags: tgt

