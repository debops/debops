Getting started
===============

.. contents::
   :local:


The management of the libvirt daemon is split into a few Ansible roles to allow
easier control over a lot of configuration options. The roles are meant to be
used together, with only the main role taking care of the environment itself.
See the example playbook provided with the main role to see how they are used
together.

The ``debops.libvirtd`` role will install :program:`libvirtd` along with virtualization
components required on the server. It manages the configuration of the main
:command:`libvirtd` daemon process. The role detects if the OpenNebula
environment is enabled using the specific Ansible inventory groups and enables
support for OpenNebula in libvirt.

The :ref:`debops.libvirtd_qemu <debops.libvirtd_qemu>` role manages the configuration of the QEMU/KVM
virtualization environment. The role supports custom configuration required by
OpenNebula nodes, which is enabled automatically when OpenNebula environment is
detected by the main role.


Example inventory
-----------------

This role should be enabled on virtualization hosts, you can do this by adding
a host to the ``[debops_service_libvirtd]`` group:

.. code:: ini

   [debops_service_libvirtd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.libvirtd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/libvirtd.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::libvirtd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
