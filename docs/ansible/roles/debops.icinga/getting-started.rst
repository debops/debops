Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.icinga`` role is not included in the ``common.yml`` playbook and
needs to be activated by adding a host to a specific Ansible inventory group.
The role is designed to be used on all hosts in the cluster, therefore the
easiest way to do this is to include the main DebOps group in the Icinga
inventory group.

.. code-block:: none

   [debops_all_hosts]
   icinga-master
   hostname1
   hostname2

   [debops_service_icinga:children]
   debops_all_hosts

See the :ref:`icinga__ref_deployment` documentation for more details about
deploying Icinga in DebOps.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.icinga`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/icinga.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::icinga``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::icinga:register``
  This tag can be used to register an Icinga 2 instance in the Icinga Director
  via the REST API. Already registered nodes are not registered again.
