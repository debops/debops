Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.icinga_web`` role is not included in the ``common.yml`` playbook
and needs to be enabled by adding a host to a specific Ansible inventory group.

The application expects a PostgreSQL or MariaDB database and won't work without
one or the other. You can install a database on the same host as the
application, or configure the :ref:`debops.postgresql` or  the
:ref:`debops.mariadb` roles to use an external database (see the documentation
of these roles for details).

It's also possible to install the Icinga 2 Web interface without the Icinga
2 Agent on the same host, however it results in a reduced functionality and
additional configuration is required to point the Web interface to an external
Icinga 2 Agent for command transport. By default the role uses the Icinga
2 Agent installed on the ``localhost`` for command transport.

See the :ref:`icinga__ref_deployment` documentation for more details about
deploying Icinga in DebOps and for a full example of Ansible inventory.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.icinga_web`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/icinga_web.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::icinga_web``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
