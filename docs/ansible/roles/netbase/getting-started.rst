Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The role is included by default in the ``bootstrap.yml`` and ``common.yml``
playbook, therefore you don't need to do anything to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.netbase`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/netbase.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::netbase``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.netbase`` Ansible role:

- Manual pages: :man:`hostname(5)`, :man:`hosts(5)`, :man:`networks(5)`
