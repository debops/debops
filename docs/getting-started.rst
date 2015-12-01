Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To configure encrypted filesystems on host given in
``debops_service_cryptsetup`` Ansible inventory group:

.. code:: ini

    [debops_service_cryptsetup]
    hostname

Example playbook
----------------

Here's an example playbook that can be used to manage cryptsetup::

    ---
    - hosts: debops_service_cryptsetup
      become: True

      roles:

        - role: debops.cryptsetup
          tags: [ 'role::cryptsetup' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::cryptsetup``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::cryptsetup:backup``
  LUKS header backup related tasks.
