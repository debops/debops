Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To manage Btrfs on host given in ``debops_service_btrfs`` Ansible inventory
group:

.. code:: ini

    [debops_service_btrfs]
    hostname

Example playbook
----------------

Here's an example playbook that can be used to manage Btrfs::

    ---
    - name: Manage Btrfs
      hosts: [ 'debops_service_btrfs' ]
      become: True

      roles:

        - role: debops-contrib.btrfs
          tags: [ 'role::btrfs' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::btrfs``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::btrfs:install``
  Tasks related to the installation of required packages.

``role::btrfs:subvolumes``
  Tasks related to managing Btrfs subvolumes.
