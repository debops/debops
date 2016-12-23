.. _cryptsetup__ref_getting_started:

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:

.. _cryptsetup__ref_overview_terminology:

Overview and terminology
------------------------

The following layers are involved in configuring an encrypted filesystem using
block device encryption:

#. Ciphertext block device: This can be any block device or partition on a block device.

#. Plaintext device mapper target: Created by `dm-crypt`_ under :file:`/dev/mapper/`.
   Opening this layer is called "mapping" or "decrypting" which means making
   the plaintext device mapper target available by loading and keeping the
   master key for the block cypher in volatile memory (RAM).

#. Plaintext mount point of the filesystem: Where the plaintext files can be accessed.
   Opening this layer is called "mounting".

.. _cryptsetup__ref_example_inventory:

Example inventory
-----------------

To configure encrypted filesystems on host given in
``debops_service_cryptsetup`` Ansible inventory group:

.. code:: ini

   [debops_service_cryptsetup]
   hostname

In case the host in question happens to be a TemplateBasedVM on `Qubes OS`_, it
should instead be added to ``debops_service_cryptsetup_persistent_paths`` so
that the changes can be made persistent:

.. code:: ini

   [debops_service_cryptsetup_persistent_paths]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cryptsetup`` role:

.. literalinclude:: playbooks/cryptsetup.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.cryptsetup`` together with the ``debops.persistent_paths`` role:

.. literalinclude:: playbooks/cryptsetup-persistent_paths.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host is first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::cryptsetup``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::cryptsetup:backup``
  LUKS header backup related tasks.
