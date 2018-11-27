Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

A host needs to be added to Ansible inventory to allow it to be bootstrapped.
The default DebOps :file:`bootstrap.yml` playbook expects the hosts to be in the
``[debops_all_hosts]`` Ansible group:

.. code-block:: none

   [debops_all_hosts]
   hostname ansible_ssh_host=hostname.example.com

You might want to set the default DNS domain used by your hosts. To do that,
set the variable below in :file:`ansible/inventory/group_vars/all/netbase.yml` or
in a similar place in inventory:

.. code-block:: yaml

   netbase__domain: 'example.com'

In this case, ``debops.netbase`` role included in the bootstrap playbook will
configure the hosts so that their Fully Qualified Domain Name will be, for
example, ``hostname.example.com`` - each host will be placed on a subdomain
inside the ``example.com`` domain.

You can also set the domain through the inventory directly, by setting it in
the host's label in the inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname.example.com

Example playbook
----------------

Here's an example playbook which uses the ``debops.bootstrap`` role:

.. literalinclude:: ../../../../ansible/playbooks/bootstrap.yml
   :language: yaml

How to bootstrap a host with DebOps
-----------------------------------

Within main DebOps playbooks, ``bootstrap`` is a separate playbook which is not
run by default by main playbook. To use it with a new host which has only
a ``root`` account and requires a password, you can run the playbook like this:

.. code-block:: console

   user@host:~$ debops bootstrap --limit host --user root --ask-pass

Bootstrap playbook does not have specific host restrictions, so it will be
executed on all hosts (apart from ``localhost``) if not limited, which you
should avoid as done in the example using ``--limit host``.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::bootstrap``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::bootstrap:packages``
  Execute tasks related to package installation.

``role::bootstrap:admin``
  Execute tasks related to setting up the admin user.

``role::bootstrap:hostname``
  Execute tasks related to configuring the hostname.
