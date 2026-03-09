.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _docker_service__ref_guides:

Deployment guides
=================

.. only:: html

   .. contents:: Sections
      :local:

This page contains ready-to-use examples for deploying popular applications
with the ``debops.docker_service`` role. Each example includes the complete
service definition, :command:`nginx` reverse proxy configuration, and a
container healthcheck where the application supports it.

The examples assume that the target host already has Docker Engine installed
via the :ref:`debops.docker_server` role and that the host is a member of both
the ``[debops_service_docker_server]`` and ``[debops_service_docker_service]``
Ansible inventory groups.


.. _docker_service__guide_bugsink:

Bugsink
-------

`Bugsink <https://www.bugsink.com/>`_ is a Sentry-compatible error tracking
server. This example deploys Bugsink with a PostgreSQL database managed by the
:ref:`debops.postgresql_server` role on the same host.

Prerequisites
~~~~~~~~~~~~~

The host must be a member of the ``[debops_service_postgresql_server]``
inventory group so that PostgreSQL is installed and configured before the
``docker_service`` playbook runs. The ``postgresql`` block in the service
definition will automatically create the database and user.

Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/bugsink.example.com/docker_service.yml
   docker_service__host_services:

     - name: 'bugsink'
       image: 'bugsink/bugsink:latest'
       ports:
         - '127.0.0.1:8000:8000'
       volumes:
         - '/srv/docker/bugsink/data:/data'
       env:
         SECRET_KEY: '{{ lookup("password", secret
                         + "/docker_service/bugsink/secret_key
                            chars=ascii_letters,digits length=50") }}'
         DATABASE_URL: 'postgresql:///bugsink?host=/var/run/postgresql'
         PORT: '8000'
         CREATE_SUPERUSER: 'admin:{{ lookup("password", secret
                                     + "/docker_service/bugsink/admin_password") }}'
       postgresql:
         database: 'bugsink'
         user: 'bugsink'
       nginx:
         enabled: true
         fqdn: 'bugsink.example.com'
         port: '8000'

.. note::

   Bugsink does not currently provide an official health check endpoint
   (`issue #98 <https://github.com/bugsink/bugsink/issues/98>`_). A basic
   HTTP check can be used as a workaround once the endpoint is available.

If the container connects to PostgreSQL over a UNIX socket, mount the socket
directory as a volume:

.. code-block:: yaml

       volumes:
         - '/srv/docker/bugsink/data:/data'
         - '/var/run/postgresql:/var/run/postgresql:ro'


.. _docker_service__guide_grafana:

Grafana
-------

`Grafana <https://grafana.com/>`_ is a popular observability dashboard. This
example deploys Grafana with persistent storage, auto-generated admin password,
and an :command:`nginx` reverse proxy.

Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/grafana.example.com/docker_service.yml
   docker_service__host_services:

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
       memory: '512m'
       healthcheck:
         test: [ 'CMD-SHELL',
                 'wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/api/health || exit 1' ]
         interval: '15s'
         timeout: '5s'
         retries: 3
         start_period: '30s'
       nginx:
         enabled: true
         fqdn: 'grafana.example.com'
         port: '3000'
         proxy_options: |
           proxy_buffering off;

Datasource provisioning
~~~~~~~~~~~~~~~~~~~~~~~

Grafana supports automatic datasource configuration through provisioning
files. Use ``config_files`` with the ``src`` parameter to render a Jinja2
template:

.. code-block:: yaml

     - name: 'grafana'
       image: 'grafana/grafana:11.0.0'
       config_files:
         - dest: '/srv/docker/grafana/provisioning/datasources/victoria.yml'
           src: 'docker_service/grafana/datasources.yml.j2'
       volumes:
         - '/srv/docker/grafana/data:/var/lib/grafana'
         - '/srv/docker/grafana/provisioning:/etc/grafana/provisioning:ro'
       # ... remaining parameters ...

The template file (e.g.
``ansible/resources/templates/by-host/hostname/docker_service/grafana/datasources.yml.j2``)
might look like:

.. code-block:: yaml

   apiVersion: 1
   datasources:
     - name: VictoriaMetrics
       type: prometheus
       access: proxy
       url: http://127.0.0.1:8428
       isDefault: true


.. _docker_service__guide_homepage:

Homepage
--------

`Homepage <https://gethomepage.dev/>`_ is a modern application dashboard with
integrations for over 100 services. This example uses ``config_dir`` to manage
multiple configuration files from a template directory.

Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/dashboard.example.com/docker_service.yml
   docker_service__host_services:

     - name: 'homepage'
       image: 'ghcr.io/gethomepage/homepage:latest'
       ports:
         - '127.0.0.1:3000:3000'
       config_dir:
         src: 'docker_service/homepage/config'
         dest: '/srv/docker/homepage/config'
       volumes:
         - '/srv/docker/homepage/config:/app/config:ro'
       env:
         HOMEPAGE_ALLOWED_HOSTS: 'dashboard.example.com'
       healthcheck:
         test: [ 'CMD-SHELL',
                 'wget --no-verbose --tries=1 --spider http://127.0.0.1:3000/api/healthcheck || exit 1' ]
         interval: '15s'
         timeout: '5s'
         retries: 3
         start_period: '20s'
       nginx:
         enabled: true
         fqdn: 'dashboard.example.com'
         port: '3000'

Template directory
~~~~~~~~~~~~~~~~~~

Create the configuration templates in your Ansible resources directory. The
``config_dir`` parameter scans the source directory using
``community.general.filetree`` and renders each file as a Jinja2 template:

.. code-block:: none

   ansible/resources/templates/by-host/dashboard.example.com/
     docker_service/homepage/config/
       settings.yaml
       services.yaml
       bookmarks.yaml
       widgets.yaml

Example ``settings.yaml``:

.. code-block:: yaml

   ---
   title: My Dashboard
   theme: dark
   color: slate
   headerStyle: clean

Example ``services.yaml``:

.. code-block:: yaml

   ---
   - Infrastructure:
     - Proxmox:
         href: https://proxmox.example.com
         icon: proxmox.svg
         description: Hypervisor
     - Grafana:
         href: https://grafana.example.com
         icon: grafana.svg
         description: Monitoring dashboard

Example ``bookmarks.yaml``:

.. code-block:: yaml

   ---
   - Development:
     - GitLab:
         - abbr: GL
           href: https://gitlab.example.com

Example ``widgets.yaml``:

.. code-block:: yaml

   ---
   - resources:
       cpu: true
       memory: true
       disk: /
   - search:
       provider: duckduckgo
       target: _blank

.. important::

   All Homepage configuration files **must** be provided through ``config_dir``.
   Because the volume is mounted read-only (``:ro``), the container cannot
   create missing files at startup. If any expected file (e.g.
   ``settings.yaml``, ``services.yaml``, ``bookmarks.yaml``, ``widgets.yaml``,
   ``docker.yaml``, ``custom.css``, ``custom.js``) is absent from the template
   directory, Homepage will fail to start. Make sure every file that Homepage
   expects is present in the source directory, even if it only contains an
   empty YAML document (``---``).

.. note::

   Homepage requires the ``HOMEPAGE_ALLOWED_HOSTS`` environment variable to
   be set when accessed through a reverse proxy. Set it to the FQDN used in
   the :command:`nginx` configuration.


.. _docker_service__guide_vaultwarden:

Vaultwarden
-----------

`Vaultwarden <https://github.com/dani-garcia/vaultwarden>`_ is a lightweight,
Bitwarden-compatible password manager server. It uses SQLite by default, so no
external database is required.

Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/vault.example.com/docker_service.yml
   docker_service__host_services:

     - name: 'vaultwarden'
       image: 'vaultwarden/server:latest'
       ports:
         - '127.0.0.1:8080:80'
       volumes:
         - '/srv/docker/vaultwarden/data:/data'
       env:
         DOMAIN: 'https://vault.example.com'
         SIGNUPS_ALLOWED: 'false'
         ADMIN_TOKEN: '{{ lookup("password", secret
                          + "/docker_service/vaultwarden/admin_token
                             chars=ascii_letters,digits length=48") }}'
       healthcheck:
         test: [ 'CMD-SHELL',
                 'wget --no-verbose --tries=1 --spider http://127.0.0.1:80/alive || exit 1' ]
         interval: '30s'
         timeout: '5s'
         retries: 3
         start_period: '15s'
       nginx:
         enabled: true
         fqdn: 'vault.example.com'
         port: '8080'
         options: |
           client_max_body_size 128m;

SMTP configuration
~~~~~~~~~~~~~~~~~~

To enable email notifications (password reset, 2FA, invitations), add SMTP
environment variables:

.. code-block:: yaml

       env:
         DOMAIN: 'https://vault.example.com'
         SIGNUPS_ALLOWED: 'false'
         ADMIN_TOKEN: '{{ lookup("password", secret
                          + "/docker_service/vaultwarden/admin_token
                             chars=ascii_letters,digits length=48") }}'
         SMTP_HOST: 'smtp.example.com'
         SMTP_FROM: 'vaultwarden@example.com'
         SMTP_PORT: '587'
         SMTP_SECURITY: 'starttls'
         SMTP_USERNAME: 'vaultwarden@example.com'
         SMTP_PASSWORD: '{{ lookup("password", secret
                            + "/docker_service/vaultwarden/smtp_password") }}'


.. _docker_service__guide_victoriametrics:

VictoriaMetrics
---------------

`VictoriaMetrics <https://victoriametrics.com/>`_ is a fast, cost-effective
time series database. This is a simple single-node deployment with an
:command:`nginx` reverse proxy providing TLS termination.

Inventory
~~~~~~~~~

.. code-block:: none

   [debops_all_hosts]
   vmetrics.example.com

   [debops_service_docker_server]
   vmetrics.example.com

   [debops_service_docker_service]
   vmetrics.example.com

Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/vmetrics.example.com/docker_service.yml
   docker_service__host_services:

     - name: 'victoriametrics'
       image: 'victoriametrics/victoria-metrics:v1.93.0'
       ports:
         - '127.0.0.1:8428:8428'
       volumes:
         - '/srv/docker/victoriametrics/data:/victoria-metrics-data'
       command: '-retentionPeriod=12 -selfScrapeInterval=10s'
       memory: '512m'
       healthcheck:
         test: [ 'CMD-SHELL',
                 'wget --no-verbose --tries=1 --spider http://127.0.0.1:8428/health || exit 1' ]
         interval: '15s'
         timeout: '5s'
         retries: 3
         start_period: '10s'
       nginx:
         enabled: true
         fqdn: 'vmetrics.example.com'
         port: '8428'

The ``-retentionPeriod=12`` flag configures a 12-month data retention period.
The ``-selfScrapeInterval=10s`` flag enables internal metrics collection.

The container binds to ``127.0.0.1`` only -- external access is provided by
:command:`nginx` with TLS termination handled by the DebOps PKI
infrastructure.


.. _docker_service__guide_victoriametrics_vmauth:

VictoriaMetrics with vmauth
---------------------------

`vmauth <https://docs.victoriametrics.com/vmauth/>`_ is an HTTP
proxy/authenticator for VictoriaMetrics. It provides authentication (Basic
Auth, Bearer tokens) and request routing. This example deploys VictoriaMetrics
together with vmauth as an authentication layer.

Two architectures are possible:

1. **vmauth behind nginx** (recommended) -- :command:`nginx` handles TLS
   termination; vmauth handles authentication and routes to VictoriaMetrics.
2. **vmauth with own TLS** -- vmauth terminates TLS directly using DebOps PKI
   certificates mounted from the host.

This guide demonstrates the recommended approach (vmauth behind :command:`nginx`).

Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/vmetrics.example.com/docker_service.yml
   docker_service__host_services:

     - name: 'victoriametrics'
       image: 'victoriametrics/victoria-metrics:v1.93.0'
       ports:
         - '127.0.0.1:8428:8428'
       volumes:
         - '/srv/docker/victoriametrics/data:/victoria-metrics-data'
       command: '-retentionPeriod=12 -selfScrapeInterval=10s'
       healthcheck:
         test: [ 'CMD-SHELL',
                 'wget --no-verbose --tries=1 --spider http://127.0.0.1:8428/health || exit 1' ]
         interval: '15s'
         timeout: '5s'
         retries: 3
         start_period: '10s'

     - name: 'vmauth'
       image: 'victoriametrics/vmauth:latest'
       ports:
         - '127.0.0.1:8427:8427'
       config_files:
         - dest: '/srv/docker/vmauth/auth.yml'
           content: |
             users:
               - username: 'metrics'
                 password: '{{ lookup("password", secret
                               + "/docker_service/vmauth/metrics_password") }}'
                 url_prefix: 'http://{{ ansible_default_ipv4.address | d("127.0.0.1") }}:8428/'
           mode: '0640'
       volumes:
         - '/srv/docker/vmauth/auth.yml:/etc/vmauth/auth.yml:ro'
       command: '-auth.config=/etc/vmauth/auth.yml'
       healthcheck:
         test: [ 'CMD-SHELL',
                 'wget --no-verbose --tries=1 --spider http://127.0.0.1:8427/health || exit 1' ]
         interval: '15s'
         timeout: '5s'
         retries: 3
         start_period: '10s'
       nginx:
         enabled: true
         fqdn: 'vmetrics.example.com'
         port: '8427'

In this setup, VictoriaMetrics does not have an ``nginx`` block -- it is only
accessible through vmauth. The :command:`nginx` reverse proxy terminates TLS
and forwards traffic to vmauth, which authenticates requests before proxying
them to VictoriaMetrics.

The ``config_files`` parameter generates the vmauth configuration file with
an auto-generated password stored in the DebOps secret directory. The file is
mounted read-only into the container.

Alternative: vmauth with own TLS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you prefer vmauth to handle TLS directly (without :command:`nginx`), mount
the DebOps PKI certificates into the container:

.. code-block:: yaml

     - name: 'vmauth'
       image: 'victoriametrics/vmauth:latest'
       ports:
         - '0.0.0.0:443:443'
       config_files:
         - dest: '/srv/docker/vmauth/auth.yml'
           content: |
             users:
               - username: 'metrics'
                 password: '{{ lookup("password", secret
                               + "/docker_service/vmauth/metrics_password") }}'
                 url_prefix: 'http://{{ ansible_default_ipv4.address | d("127.0.0.1") }}:8428/'
           mode: '0640'
       volumes:
         - '/srv/docker/vmauth/auth.yml:/etc/vmauth/auth.yml:ro'
         - '/etc/pki/realms/domain/default.crt:/etc/vmauth/cert.pem:ro'
         - '/etc/pki/realms/domain/default.key:/etc/vmauth/key.pem:ro'
       command: >-
         -auth.config=/etc/vmauth/auth.yml
         -tls -tlsCertFile=/etc/vmauth/cert.pem -tlsKeyFile=/etc/vmauth/key.pem
         -httpListenAddr=:443

The certificate paths (``/etc/pki/realms/domain/``) are managed by the
:ref:`debops.pki` role. vmauth automatically reloads certificates when they
change on disk, so no container restart is needed for certificate renewal.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
