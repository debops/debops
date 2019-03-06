Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To install Docker Registry on a host, you need to add it to the
``[debops_service_docker_registry]`` Ansible inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_redis_server]
   hostname

   [debops_service_docker_registry]
   hostname

The support for Redis Server is optional, and not required on the same host.

The :ref:`debops.docker_registry` role is designed to integrate well with the
:ref:`debops.gitlab` role, to provide backend support for the GitLab Container
Registry service. See the role documentation for more details.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.docker_registry`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/docker_registry.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::docker_registry``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.docker_registry``
Ansible role:

- `Docker Registry configuration`__ documentation

.. __: https://docs.docker.com/registry/configuration/

- `GitLab Container Registry`__ documentation

.. __: https://gitlab.com/help/user/project/container_registry
