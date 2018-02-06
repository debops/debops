Getting started
===============

.. contents::
   :local:


Default configuration
---------------------


@TODO


Example inventory
-----------------

``debops.prosody`` is included by default in the :file:`common.yml` DebOps playbook;
To enable it, add a host to the group `[debops_service_prosody]`.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.prosody`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/prosody.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prosody``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
``role::ferm``
  Role tag for configure the firewall ferm.
