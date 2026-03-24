.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents:: Sections
      :local:


Prerequisites
-------------

The ``debops.docker_compose_service`` role requires Docker Engine to be already
installed on the host. Use the :ref:`debops.docker_server` role to set up
Docker before using this role. The host must be included in both the
``[debops_service_docker_server]`` and
``[debops_service_docker_compose_service]`` Ansible inventory groups.

The role uses the ``community.docker`` Ansible collection (specifically the
``docker_compose_v2`` and ``docker_compose_v2_pull`` modules) to manage Compose
projects. The ``python3-docker`` package is installed automatically to provide
the required Python bindings.

The role imports the :ref:`debops.secret` role to provide access to the
``secret`` variable. This allows service definitions to use the
``lookup("password", ...)`` plugin to auto-generate and store secrets in
the DebOps secret directory on the Ansible Controller.

Docker Compose projects managed by this role require a ``docker-compose.yml``
file, which is typically provided as a Jinja2 template via the
``compose_src`` parameter. Templates are resolved against the Ansible
``templates/`` search path, allowing per-host customization through the
DebOps resources directory.


Default setup
-------------

If you don't specify any configuration, the role will not create any Compose
projects. You need to define at least one service entry with ``name`` and
either ``compose_src`` or ``compose_content`` parameters.

Each service entry represents a Docker Compose project. The role creates a
project directory, generates the ``docker-compose.yml`` and ``.env`` files,
deploys any additional configuration files, and then runs ``docker compose
up -d`` to bring the project up.

When a service has an ``nginx`` block with ``enabled: true``, the role
automatically configures an :command:`nginx` reverse proxy virtual host that
forwards traffic to the container. SSL/TLS is handled by the DebOps PKI
infrastructure.

For a complete deployment example of Immich (a self-hosted photo and video
management solution), see the :ref:`docker_compose_service__ref_guides` page.


Comparison with debops.docker_service
-------------------------------------

The :ref:`debops.docker_service` role manages **individual Docker containers**
through the ``community.docker.docker_container`` Ansible module. It works well
for single-container applications like Grafana, VictoriaMetrics, or Bugsink.

The ``debops.docker_compose_service`` role manages **Docker Compose projects**
-- groups of related containers defined in a ``docker-compose.yml`` file and
managed as a unit through ``docker compose up/down``. This is necessary for
applications like Immich that consist of multiple interdependent containers
(application server, machine learning, database, cache) and rely on Compose
features such as service discovery, ``depends_on`` with health checks, and
``extends`` for hardware acceleration overlays.

Choose ``debops.docker_service`` for simple, single-container services and
``debops.docker_compose_service`` for multi-container applications distributed
as Compose files.


Nginx reverse proxy
-------------------

The role integrates with :ref:`debops.nginx` to automatically set up reverse
proxy virtual hosts for Compose services. For each service with ``nginx``
configuration, the role generates:

- An :command:`nginx` upstream pointing to ``127.0.0.1:<port>``
- A server block with the specified FQDN, proxying to the upstream

The Compose project should expose the relevant port on ``127.0.0.1`` (or
configure the service to listen on localhost). The :command:`nginx` reverse
proxy then handles external access with SSL termination.


Example inventory
-----------------

To deploy Docker Compose services on a host, it needs to be included in the
appropriate Ansible inventory groups:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_docker_server]
   hostname

   [debops_service_docker_compose_service]
   hostname


Minimal service example
-----------------------

Deploy a simple application from a Compose template with an :command:`nginx`
reverse proxy:

.. code-block:: yaml

   # ansible/inventory/host_vars/hostname/docker_compose_service.yml
   docker_compose_service__host_services:

     - name: 'myapp'
       compose_src: 'docker_compose_service/myapp/docker-compose.yml'
       env:
         APP_VERSION: 'latest'
         APP_SECRET: '{{ lookup("password", secret
                         + "/docker_compose_service/myapp/secret
                            chars=ascii_letters,digits length=32") }}'
       nginx:
         enabled: true
         fqdn: 'myapp.example.com'
         port: '8080'

The Compose file template would be placed at:

.. code-block:: none

   ansible/resources/templates/by-host/hostname/
     docker_compose_service/myapp/docker-compose.yml


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.docker_compose_service`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/docker_compose_service.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::docker_compose_service``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::docker_compose_service:config``
  Tasks related to creating project directories, generating Compose files,
  environment files and configuration files (``config_files`` and
  ``config_dir``).

``role::docker_compose_service:compose``
  Tasks related to pulling Docker images and bringing Compose projects up
  or down.
