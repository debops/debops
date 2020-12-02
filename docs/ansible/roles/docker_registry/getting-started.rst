.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C)      2020 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2019-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

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
   :lines: 1,5-


Authentication
--------------

:envvar:`docker_registry__basic_auth_except_get` allows an easy yet auditable
write access control to the registry. To use it, set the variable to ``True``.
Additionally, you need to define the hosts or networks to require authentication for.
This is basically a workaround because the Docker Server first does a GET
request and if it goes though, it will not provide authentication. But we
always allow read only requests without authentication so we need to force
authentication like this:

.. code-block:: yaml

   nginx__custom_config:
     - name: 'geo_force_authentication'
       custom: |
         ## This is not security related. It just triggers Docker that it may authenticate itself.
         geo $force_authentication {
           default 0;
           2001:db8:2342::/64 1;
         }

Then define the users which should be created and allowed write access:

.. code-block:: yaml

   docker_registry__basic_auth_users:
     - 'build-docker-debian-base-image'

Refer to :ref:`debops.secret` for details.

You can then use :command:`docker login docker-registry.example.net` to login. This step is manually for now.


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
