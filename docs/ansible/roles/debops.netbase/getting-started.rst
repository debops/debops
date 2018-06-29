Getting started
===============

.. contents::
   :local:


Host and network database bootstrapping
---------------------------------------

Since the role is not included directly in the :file:`common.yml` playbook, if
you need to configure the host database before the common playbook is applied,
you can execute the role before the common or site playbook:

.. code-block:: console

   debops service/netbase -l <hosts> && debops common -l <hosts>


Example inventory
-----------------

To enable support for the ``debops.netbase`` role, the host(s) need to be
included in the ``[debops_service_netbase]`` Ansible inventory group:

.. code-block:: none

   [debops_service_netbase]
   hostname

A common practice is to maintain the same host and network database across
multiple hosts in a cluster. To do that effectively, you can use inventory
parent/children groups to, for example, enable the role on all DebOps-managed
hosts:

.. code-block:: none

   [debops_service_netbase:children]
   debops_all_hosts


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

- Manual pages: :man:`hosts(5)`, :man:`networks(5)`
