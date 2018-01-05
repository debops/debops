Getting started
===============

.. contents::
   :local:


This role is part of the DebOps libvirtd configuration
------------------------------------------------------

The ``debops.libvirtd_qemu`` role manages the libvirtd QEMU-related
configuration. It can be used as standalone, however the role is intentionally
very limited and relies on the :ref:`debops.libvirtd` to do most of the
work related to package installation and environment setup. You are strongly
advised to use the roles and their playbooks together.


Example inventory
-----------------

The role is used by the :ref:`debops.libvirtd` playbook and will be enabled
automatically on hosts that are included in the ``[debops_service_libvirtd]``
Ansible inventory group.

This role can be enabled on virtualization hosts separately. You can do this by
adding a host to the ``[debops_service_libvirtd_qemu]`` group:

.. code:: ini

   [debops_service_libvirtd_qemu]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.libvirtd_qemu`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/libvirtd_qemu.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::libvirtd_qemu``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
