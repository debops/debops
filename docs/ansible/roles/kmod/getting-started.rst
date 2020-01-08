Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To manage kernel modules on a host, you need to add it to the
``[debops_service_kmod]`` Ansible inventory group:

.. code-block:: none

   [debops_service_kmod]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.kmod`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/kmod.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::kmod``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.kmod`` Ansible role:

- Manual pages: :man:`modprobe.d(5)`, :man:`modules-load.d(5)`
- `Linux Kernel Modules`__ page on Debian Wiki
- `Kernel Modules`__ page on Arch Wiki

.. __: https://wiki.debian.org/Modules
.. __: https://wiki.archlinux.org/index.php/kernel_modules
