Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.debops_legacy`` role doesn't need to be enabled in Ansible
inventory, since its playbook by default works against the hosts in the
``[debops_all_hosts]`` Ansible inventory group. However the role is not
included in the ``site.yml`` playbook and needs to be executed specifically by
the system administrator to perform work.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.debops_legacy`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/debops_legacy.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::debops_legacy``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
