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


Persistent data directories
----------------------------

For backward compatibility, the role automatically creates host directories
for bind-mount sources listed in a service's ``volumes`` parameter. This is
convenient for simple cases, but it is an *inference* -- the role has no way
to know whether a given ``volumes`` entry is meant to be a directory or a
file, so it always creates a directory. This works until a bind mount's
source is legitimately a file or socket (e.g. ``/etc/localtime``, a UNIX
socket), or a service needs specific ownership/permissions on the host
directory that ``volumes`` cannot express.

Prefer declaring host directories explicitly with ``data_dirs`` instead:

.. code-block:: yaml

   docker_service__host_services:

     - name: 'vaultwarden'
       image: 'vaultwarden/server:1.37.1-alpine'
       data_dirs:
         - path: '/srv/docker/vaultwarden/data'
           owner: 'root'
           group: 'root'
           mode: '0750'
       volumes:
         - '/srv/docker/vaultwarden/data:/data'

See :ref:`docker_service__ref_services` for the full ``data_dirs`` and
``create_volume_dirs`` syntax.


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


Custom hooks
------------

The role exposes two custom tasklists which let you execute additional Ansible
tasks before and after the role's own tasks, without modifying the role itself.
They are sourced through the :ref:`debops.debops.task_src <debops.ansible_plugins>`
lookup plugin, so you can override them at the project level by creating a file
with the same relative path under the directory configured by
``override_paths.tasks_path`` (by default
:file:`ansible/overrides/tasks/docker_service/`).

``docker_service/pre_main.yml``
  Tasks executed **before** the main role tasks, right after the
  :ref:`debops.secret` role is imported and **before** the first task that
  consumes :envvar:`docker_service__combined_services`. This is the place to
  prepare anything the combined service list depends on -- for example to
  pre-create a secret file referenced by a ``lookup("file", ...)`` inside a
  service ``env`` entry, so that the lookup does not fail on a fresh install
  before the value has been generated.

``docker_service/post_main.yml``
  Tasks executed **after** all main role tasks, once the containers have been
  created and started. This is the place to act on the running containers --
  for example to provision an application account or generate an API token by
  running a management command inside a freshly started container.

The role ships empty stub files for both tasklists, so the lookup always
resolves and the role behaves identically when no project override is present.

.. note::

   The custom tasklists are included for **every** host that runs the role.
   When a tasklist applies only to specific hosts, guard its tasks with an
   appropriate condition (for example ``when: inventory_hostname == '...'``),
   exactly like the custom tasklists of other DebOps roles.

.. note::

   Both ``include_tasks`` directives carry ``tags: [ 'always' ]``, so they are
   evaluated even when Ansible is invoked with ``--tags`` or ``--skip-tags``.
   Tag filtering is then applied to the individual tasks **inside** the hook
   file. This means you can assign your own tags to blocks or tasks in
   ``pre_main.yml`` / ``post_main.yml`` and target them directly with
   ``--tags``. For example, if the hook file contains:

   .. code-block:: yaml

      - name: Provision application accounts
        tags: [ 'myapp::accounts' ]
        block:
          # ...

   you can run only those tasks with:

   .. code-block:: console

      debops run service/docker_service --tags myapp::accounts


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
