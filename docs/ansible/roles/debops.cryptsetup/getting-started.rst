.. _cryptsetup__ref_getting_started:

Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:

.. _cryptsetup__ref_overview_terminology:

Overview and terminology
------------------------

.. When using terminology as defined here in the docs, they should be referred
   to like `plaintext device mapper target`.

The following layers are involved in configuring an encrypted filesystem using
block device encryption:

#. Ciphertext block device: This can be any block device or partition on a block device.
   It can also be a regular file which will be mapped to a block device using ``loop`` by cryptsetup.

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

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cryptsetup`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/cryptsetup-plain.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.cryptsetup`` together with the debops.persistent_paths_ role:

.. literalinclude:: ../../../../ansible/playbooks/service/cryptsetup-persistent_paths.yml
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

:ref:`debops.persistent_paths` support
--------------------------------------

In case the host in question happens to be a TemplateBasedVM on `Qubes OS`_ or
another system where persistence is not the default, it should be absent in
``debops_service_cryptsetup`` and instead be added to the
``debops_service_cryptsetup_persistent_paths`` Ansible inventory group
so that the changes can be made persistent:

.. code:: ini

   [debops_service_cryptsetup_persistent_paths]
   hostname

Besides that, the :envvar:`cryptsetup__base_packages` are expected to be
present (typically installed in the TemplateVM).

Note that even if the same filesystem is bind mounted to different locations
they are considered different file systems by :command:`mv` which would case
it fall back to content copying instead of just metadata updating.
Be sure to always access the plaintext mount point by one path if you care about this.
So either :envvar:`cryptsetup__mountpoint_parent_directory` or
`/rw/bind-dirs/media/` on Qubes OS.
