Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

The role will detect presence of a MariaDB database server and use it if
available. If not, a SQLite database will be automatically configured on the
server. You can configure MariaDB database using the :ref:`debops.mariadb_server`
Ansible role.


Example inventory
-----------------

To install and configure Etherpad on a host, it needs to be present in the
``[debops_service_etherpad]`` Ansible inventory group:

.. code-block:: none

   [debops_service_etherpad]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.etherpad`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/etherpad.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::etherpad``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::etherpad:source``
  Run tasks related to install Etherpad from source.

``role::etherpad:config``
  Run tasks related to configuring Etherpad.

``role::etherpad:plugins``
  Run tasks which install the defined Etherpad plugins.

``role::etherpad:api:call``
  Run tasks API call tasks. Can be used for rapid API calls.

``role::etherpad:api``
  Same as ``role::etherpad:api:call`` but ensures that the service is running
  and waiting for it to start before trying.
