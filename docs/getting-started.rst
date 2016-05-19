Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

``debops.ntp`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

Example playbook
----------------

Here's an example playbook for using the role without the DebOps playbook:

.. code-block:: yaml

   - name: Manage Network Time Protocol service
     hosts: [ 'debops_all_hosts', 'debops_service_ntp' ]
     become: True

     roles:

       - role: debops.ferm
         tags: [ 'role::ferm' ]
         ferm__dependent_rules:
           - '{{ ntp__ferm__dependent_rules }}'

       - role: debops.ntp
         tags: [ 'role::ntp' ]

