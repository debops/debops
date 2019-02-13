Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

The ``debops.ferm`` role is part of the default DebOps playbook an run on
all hosts which are part of the ``[debops_all_hosts]`` group. To use this
role with DebOps it's therefore enough to add your host to the mentioned
host group (which most likely it is already)::

    [debops_all_hosts]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops.ferm`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/ferm.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::ferm``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::ferm:custom_files``
  Copy custom ferm configuration files to remote hosts.

``role::ferm:rules``
  Run tasks to add or remove ferm rules and configure IP packet forwarding.
