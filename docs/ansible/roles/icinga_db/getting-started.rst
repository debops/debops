Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.icinga_db`` role is used with the main :ref:`debops.icinga` role
to configure the database for Icinga 2, and will not work correctly otherwise.
Database configuration is performed using the ``dbconfig`` configuration
management support available in Debian.  Both PostgreSQL and MariaDB databases
are supported and automatically selected if present.

.. code-block:: none

   [debops_service_icinga]
   icinga-master

   [debops_service_icinga_db]
   icinga-master

See the :ref:`icinga__ref_deployment` documentation for more details about
deploying Icinga in DebOps.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.icinga_db`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/icinga_db.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::icinga_db``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
