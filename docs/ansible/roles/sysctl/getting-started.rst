Getting started
===============

.. contents::
   :local:

.. include:: ../../../includes/global.rst

Example inventory
-----------------

The ``debops.sysctl`` role is included by default in the `DebOps common
playbook`_ and you don't need to add hosts to a custom inventory group to
activate the role.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.sysctl`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/sysctl.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::sysctl``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
