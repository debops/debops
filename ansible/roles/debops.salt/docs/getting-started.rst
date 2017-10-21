Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

To enable management of the Salt Master service, a given host needs to be added
to the ``[debops_service_salt]`` Ansible inventory group:

.. code-block:: none

   [debops_service_salt]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.salt`` role:

.. literalinclude:: playbooks/salt.yml
   :language: yaml
