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

The ``debops.docker_service`` role requires Docker Engine to be already
installed on the host. Use the :ref:`debops.docker_server` role to set up
Docker before using this role. The host must be included in both the
``[debops_service_docker_server]`` and ``[debops_service_docker_service]``
Ansible inventory groups.

The role uses the ``community.docker`` Ansible collection to manage containers.
The ``python3-docker`` package is installed automatically to provide the
required Python bindings.

The role imports the :ref:`debops.secret` role to provide access to the
``secret`` variable. This allows service definitions to use the
``lookup("password", ...)`` plugin to auto-generate and store secrets in
the DebOps secret directory on the Ansible Controller.


Default setup
-------------

If you don't specify any configuration, the role will not create any containers.
You need to define at least one service entry with ``name`` and ``image``
parameters.

When a service has an ``nginx`` block with ``enabled: true``, the role
automatically configures an :command:`nginx` reverse proxy virtual host that
forwards traffic to the container. SSL/TLS is handled by the DebOps PKI
infrastructure.

For complete deployment examples of popular applications (Grafana,
VictoriaMetrics, Vaultwarden, Bugsink, Homepage and more), see the
:ref:`docker_service__ref_guides` page.


Nginx reverse proxy
-------------------

The role integrates with :ref:`debops.nginx` to automatically set up reverse
proxy virtual hosts for container services. For each service with ``nginx``
configuration, the role generates:

- An :command:`nginx` upstream pointing to ``127.0.0.1:<port>``
- A server block with the specified FQDN, proxying to the upstream

The container must expose the relevant port on ``127.0.0.1`` for this to work.
A typical port mapping looks like ``127.0.0.1:8428:8428``, which binds the
container port to localhost only -- :command:`nginx` then handles external
access with SSL termination.


Example inventory
-----------------

To deploy Docker container services on a host, it needs to be included in the
appropriate Ansible inventory groups:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_docker_server]
   hostname

   [debops_service_docker_service]
   hostname


Minimal service example
-----------------------

Deploy a VictoriaMetrics time series database with :command:`nginx` reverse
proxy:

.. code-block:: yaml

   # ansible/inventory/host_vars/hostname/docker_service.yml
   docker_service__host_services:

     - name: 'victoriametrics'
       image: 'victoriametrics/victoria-metrics:v1.93.0'
       ports:
         - '127.0.0.1:8428:8428'
       volumes:
         - '/srv/docker/victoriametrics/data:/victoria-metrics-data'
       command: '-retentionPeriod=12 -selfScrapeInterval=10s'
       nginx:
         enabled: true
         fqdn: 'vmetrics.example.com'
         port: '8428'


Multiple services example
-------------------------

Deploy VictoriaMetrics and Grafana side by side:

.. code-block:: yaml

   docker_service__host_services:

     - name: 'victoriametrics'
       image: 'victoriametrics/victoria-metrics:v1.93.0'
       ports:
         - '127.0.0.1:8428:8428'
       volumes:
         - '/srv/docker/victoriametrics/data:/victoria-metrics-data'
       command: '-retentionPeriod=12 -selfScrapeInterval=10s'
       memory: '512m'
       nginx:
         enabled: true
         fqdn: 'vmetrics.example.com'
         port: '8428'

     - name: 'grafana'
       image: 'grafana/grafana:11.0.0'
       ports:
         - '127.0.0.1:3000:3000'
       volumes:
         - '/srv/docker/grafana/data:/var/lib/grafana'
       env:
         GF_SERVER_ROOT_URL: 'https://grafana.example.com'
         GF_SECURITY_ADMIN_PASSWORD: '{{ lookup("password", secret
                                         + "/docker_service/grafana/admin_password") }}'
       nginx:
         enabled: true
         fqdn: 'grafana.example.com'
         port: '3000'


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.docker_service`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/docker_service.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::docker_service``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::docker_service:config``
  Tasks related to creating persistent data directories, generating
  configuration files (``config_files`` and ``config_dir``), and restarting
  containers when configuration changes.

``role::docker_service:containers``
  Tasks related to pulling Docker images and managing containers.
