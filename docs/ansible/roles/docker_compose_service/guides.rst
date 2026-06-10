.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _docker_compose_service__ref_guides:

Deployment guides
=================

.. only:: html

   .. contents:: Sections
      :local:

This page contains ready-to-use examples for deploying applications with the
``debops.docker_compose_service`` role. Each example includes the complete
service definition, Compose file template, :command:`nginx` reverse proxy
configuration, and notes on application-specific requirements.

The examples assume that the target host already has Docker Engine installed
via the :ref:`debops.docker_server` role and that the host is a member of both
the ``[debops_service_docker_server]`` and
``[debops_service_docker_compose_service]`` Ansible inventory groups.


.. _docker_compose_service__guide_immich:

Immich
------

`Immich <https://immich.app/>`_ is a self-hosted photo and video management
solution. It provides automatic backup from mobile devices, facial recognition,
smart search, and hardware-accelerated video transcoding.

Immich consists of multiple interdependent services that are deployed together
as a Docker Compose project:

- **immich-server** -- the main application server (API + web UI, port 2283)
- **immich-machine-learning** -- facial recognition, smart search, OCR
- **database** -- PostgreSQL with the ``vectorchord`` extension for AI search
- **redis** -- Valkey (Redis-compatible) cache for job queues

The official Immich PostgreSQL image bundles the ``vectorchord`` and
``pgvecto.rs`` extensions that are not available in standard Debian packages.
For this reason, the database is kept inside the Compose project rather than
managed by the :ref:`debops.postgresql_server` role.


Architecture
~~~~~~~~~~~~

.. code-block:: none

   Internet
       |
   [nginx reverse proxy]  -- TLS termination (DebOps PKI)
       |
   127.0.0.1:2283
       |
   [immich-server]  -- main app (API + microservices)
       |           \
       |        [immich-machine-learning]  -- ML inference (GPU optional)
       |
   [database]       [redis]
   PostgreSQL        Valkey
   + vectorchord

The :command:`nginx` reverse proxy is managed by the :ref:`debops.nginx` role
through the built-in integration. The Compose project does not expose any ports
to the network -- :command:`nginx` connects to the Immich server on
``127.0.0.1:2283``.


Prerequisites
~~~~~~~~~~~~~

The host must be a member of the following inventory groups:

.. code-block:: none

   [debops_service_docker_server]
   immich.example.com

   [debops_service_docker_compose_service]
   immich.example.com

   [debops_service_nginx]
   immich.example.com

   [pki_acme_cloudflare]
   immich.example.com

Hardware requirements:

- Minimum 4 CPU cores and 6 GB RAM (8 GB recommended for ML)
- SSD/NVMe storage for the PostgreSQL database
- Separate storage (NAS/NFS) recommended for photo/video library
- GPU access (``/dev/dri``) is optional but improves ML and transcoding
  performance significantly


Inventory
~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/hosts_immich.yml
   serwery_immich:
     hosts:
       immich.example.com:

   debops_all_hosts:
     children:
       serwery_immich:

   debops_service_zabbix_agent:
     children:
       serwery_immich:

   debops_service_docker_server:
     children:
       serwery_immich:

   debops_service_docker_compose_service:
     children:
       serwery_immich:

   debops_service_nginx:
     children:
       serwery_immich:

   pki_acme_cloudflare:
     children:
       serwery_immich:


Docker server
~~~~~~~~~~~~~

Configure Docker to use upstream packages:

.. code-block:: yaml

   # ansible/inventory/host_vars/immich.example.com/docker_server.yml
   ---

   docker_server__upstream: True


Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/immich.example.com/docker_compose_service.yml
   ---

   immich__db_password: "{{ lookup('password', secret
                            + '/docker_compose_service/immich/db_password
                               length=32 chars=ascii_letters,digits') }}"

   docker_compose_service__host_services:

     - name: 'immich'
       compose_src: 'immich/docker-compose.yml'
       env:
         UPLOAD_LOCATION: '/mnt/photo'
         DB_DATA_LOCATION: '/srv/docker/immich/postgres'
         IMMICH_VERSION: 'release'
         DB_PASSWORD: '{{ immich__db_password }}'
         DB_USERNAME: 'postgres'
         DB_DATABASE_NAME: 'immich'
       nginx:
         enabled: true
         fqdn: 'immich.example.com'
         port: '2283'
         proxy_options: |
           proxy_buffering off;
           client_max_body_size 50G;
           proxy_read_timeout 600s;
           proxy_send_timeout 600s;
           send_timeout 600s;
         options: |
           location /api/socket.io {
               proxy_pass http://immich-upstream;
               proxy_http_version 1.1;
               proxy_set_header Upgrade $http_upgrade;
               proxy_set_header Connection "upgrade";
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }

The ``immich__db_password`` variable is auto-generated and stored in the DebOps
:file:`secret/` directory. The ``UPLOAD_LOCATION`` should point to a directory
with sufficient storage for photos and videos (typically an NFS mount from
a NAS).

The :command:`nginx` configuration includes special handling for WebSocket
connections (``/api/socket.io``) and a large ``client_max_body_size`` to support
uploading high-resolution photos and videos.


Compose file template
~~~~~~~~~~~~~~~~~~~~~

Place the Compose file template in the DebOps resources directory:

.. code-block:: none

   ansible/docker_compose_service/by-host/immich.example.com/
     immich/docker-compose.yml

The template is based on the official Immich ``docker-compose.yml`` with
modifications for the DebOps environment (no external port mapping, GPU
passthrough for ML):

.. code-block:: yaml

   # {{ ansible_managed }}
   name: immich

   services:
     immich-server:
       container_name: immich_server
       image: ghcr.io/immich-app/immich-server:${IMMICH_VERSION:-release}
       volumes:
         - ${UPLOAD_LOCATION}:/data
         - /etc/localtime:/etc/localtime:ro
       env_file:
         - .env
       ports:
         - '127.0.0.1:2283:2283'
       depends_on:
         - redis
         - database
       restart: always
       healthcheck:
         disable: false

     immich-machine-learning:
       container_name: immich_machine_learning
       image: ghcr.io/immich-app/immich-machine-learning:${IMMICH_VERSION:-release}
       volumes:
         - model-cache:/cache
       env_file:
         - .env
       restart: always
       healthcheck:
         disable: false

     redis:
       container_name: immich_redis
       image: docker.io/valkey/valkey:8-bookworm
       healthcheck:
         test: redis-cli ping || exit 1
       restart: always

     database:
       container_name: immich_postgres
       image: ghcr.io/immich-app/postgres:14-vectorchord0.4.3-pgvectors0.2.0
       environment:
         POSTGRES_PASSWORD: ${DB_PASSWORD}
         POSTGRES_USER: ${DB_USERNAME}
         POSTGRES_DB: ${DB_DATABASE_NAME}
         POSTGRES_INITDB_ARGS: '--data-checksums'
       volumes:
         - ${DB_DATA_LOCATION}:/var/lib/postgresql/data
       restart: always
       healthcheck:
         disable: false

   volumes:
     model-cache:

.. important::

   The Immich server binds to ``127.0.0.1:2283`` only -- :command:`nginx`
   handles external access. Do not expose the port to ``0.0.0.0``.


GPU acceleration
~~~~~~~~~~~~~~~~

Immich can use GPU hardware for both machine learning (facial recognition,
smart search) and video transcoding. On hosts with an AMD or Intel GPU
(exposed as ``/dev/dri`` in the LXC container), add device passthrough to the
relevant services in the Compose template:

For **machine learning** (AMD ROCm/OpenCL):

.. code-block:: yaml

     immich-machine-learning:
       container_name: immich_machine_learning
       image: ghcr.io/immich-app/immich-machine-learning:${IMMICH_VERSION:-release}-openvino
       devices:
         - /dev/dri:/dev/dri
       volumes:
         - model-cache:/cache
       env_file:
         - .env
       restart: always

Use the ``-openvino`` image tag for Intel GPUs, ``-cuda`` for NVIDIA, or
``-rocm`` for AMD.

For **hardware transcoding** (VAAPI):

.. code-block:: yaml

     immich-server:
       container_name: immich_server
       image: ghcr.io/immich-app/immich-server:${IMMICH_VERSION:-release}
       devices:
         - /dev/dri:/dev/dri
       # ... remaining parameters ...

After deploying with GPU passthrough, enable hardware transcoding in the Immich
admin panel under **Administration > Video Transcoding > Hardware
Acceleration**.

.. note::

   The LXC container must be configured with GPU device passthrough. In
   OpenTofu/Proxmox, this is done via the ``device_passthrough`` parameter::

       device_passthrough = [
         { path = "/dev/dri/card0", mode = "0666", gid = 44 },
         { path = "/dev/dri/renderD128", mode = "0666", gid = 104 },
       ]


Storage
~~~~~~~

Immich stores two types of data with different performance requirements:

- **Photo/video library** (``UPLOAD_LOCATION``) -- large files, sequential
  I/O. A NAS/NFS mount is ideal. This is typically a TrueNAS dataset mounted
  into the LXC container.

- **PostgreSQL database** (``DB_DATA_LOCATION``) -- small files, random I/O.
  Must be on local SSD/NVMe storage. Network shares are **not supported** for
  the database.

When the LXC container has an NFS mount (e.g. ``/mnt/photo`` from TrueNAS),
set ``UPLOAD_LOCATION`` to that mount point. Keep ``DB_DATA_LOCATION`` on local
storage (e.g. ``/srv/docker/immich/postgres``).


Upgrading
~~~~~~~~~

To upgrade Immich, simply re-run the playbook. If ``pull`` is ``True``
(default), the role will pull the latest images and recreate the Compose
project:

.. code-block:: console

   $ debops run service/docker_compose_service --limit immich.example.com

To pin a specific version, set ``IMMICH_VERSION`` in the ``env`` dictionary:

.. code-block:: yaml

       env:
         IMMICH_VERSION: 'v2.5.0'
         # ...

.. important::

   Always check the `Immich release notes
   <https://github.com/immich-app/immich/releases>`_ before upgrading. Some
   releases require database migrations or configuration changes.


Initial setup
~~~~~~~~~~~~~

After the first deployment, open ``https://immich.example.com`` in a browser
to create the initial admin account. No additional command-line steps are
required -- Immich handles database migrations automatically on first start.


.. _docker_compose_service__guide_paperless:

Paperless-ngx with host PostgreSQL/Redis and AI sidecars
--------------------------------------------------------

`Paperless-ngx <https://docs.paperless-ngx.com/>`_ is a self-hosted document
management system that scans, OCRs, indexes and tags documents. This example is
a more advanced deployment that exercises several role features at once:

- the database and cache run **on the host** (managed by the
  :ref:`debops.postgresql_server` and :ref:`debops.redis_server` roles) and are
  reached through **UNIX sockets** bind-mounted into the container -- not as
  Compose services;
- two **AI sidecars** share the Compose project: ``paperless-gpt`` (vision OCR
  and tagging) and ``paperless-ai`` (classification and RAG chat);
- the sidecars authenticate to Paperless with **dedicated Django service
  accounts** whose API tokens are bootstrapped by the role's
  :ref:`pre_main / post_main custom tasks <docker_compose_service__ref_custom_tasks>`;
- the main UI is proxied by :command:`nginx`, while the sidecar UIs are exposed
  on LAN-only virtual hosts.

This guide focuses on the parts that differ from the simpler
:ref:`Immich <docker_compose_service__guide_immich>` example; adapt names,
domains and model choices to your environment.


Architecture
~~~~~~~~~~~~

.. code-block:: none

   [nginx]  -- TLS termination (DebOps PKI)
       |  paperless.example.com -> 127.0.0.1:8000
       |  paperless-gpt.example.com (LAN only) -> 127.0.0.1:8080
       |  paperless-ai.example.com  (LAN only) -> 127.0.0.1:3000
       |
   +-- Compose project "paperless" ---------------------------------+
   |   [webserver] paperless-ngx        [gotenberg]   [tika]        |
   |       |  (UNIX sockets, bind-mounted from host)                 |
   |   [paperless-gpt] -> webserver:8000   (vision OCR / tagging)    |
   |   [paperless-ai]  -> webserver:8000   (classification / RAG)    |
   +----------------------------------------------------------------+
       |                         |
   /var/run/postgresql       /var/run/redis        (host sockets)
   PostgreSQL                Redis
   (debops.postgresql_server)(debops.redis_server)

Unlike Immich (which keeps PostgreSQL inside the Compose project), Paperless
uses the standard Debian PostgreSQL and Redis managed by DebOps on the host.
The container talks to them over UNIX sockets, so no TCP port or extra network
namespace is involved.


Prerequisites
~~~~~~~~~~~~~

.. code-block:: none

   [debops_service_docker_server]
   paperless.example.com

   [debops_service_docker_compose_service]
   paperless.example.com

   [debops_service_postgresql_server]
   paperless.example.com

   [debops_service_postgresql]
   paperless.example.com

   [debops_service_redis_server]
   paperless.example.com

   [debops_service_nginx]
   paperless.example.com

Two PostgreSQL roles are involved, and both are required:

- :ref:`debops.postgresql_server` (group ``[debops_service_postgresql_server]``)
  installs and manages the PostgreSQL **server** on the host.
- :ref:`debops.postgresql` (group ``[debops_service_postgresql]``) manages the
  application **role and database** -- see `PostgreSQL role and database`_
  below.

The ``service/docker_compose_service`` playbook does not apply either
PostgreSQL role, so make sure their playbooks run before (or together with) the
Compose deployment, for example via ``debops run site`` or by running
``service/postgresql_server`` and ``service/postgresql`` first.


PostgreSQL role and database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The database role and database are created by the :ref:`debops.postgresql`
role, **not** inside the Compose project (this is the main difference from the
:ref:`Immich <docker_compose_service__guide_immich>` example, which keeps
PostgreSQL as a Compose service):

.. code-block:: yaml

   # host_vars/paperless.example.com/postgresql.yml
   ---

   postgresql__roles:
     - name: 'paperless'

   postgresql__databases:
     - name: 'paperless'
       owner: 'paperless'

The :ref:`debops.postgresql` role generates the role's password once and stores
it in the DebOps secret directory at::

   secret/postgresql/<inventory_hostname>/<port>/credentials/paperless/password

The Compose service definition reads that **same** path back with a
``lookup("password", ...)`` (the ``paperless__postgresql_password`` variable
below), so the database owner and the application share a single password
without copying it by hand. Because the ``service/docker_compose_service``
playbook does not apply the ``postgresql`` role, the lookup hard-codes the path
and the password parameters (``length``, ``chars``); keep them identical to the
:ref:`debops.postgresql` role defaults so both sides derive the same value.


Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # host_vars/paperless.example.com/docker_compose_service.yml
   ---

   paperless__postgresql_password: "{{ lookup('password', secret
       + '/postgresql/' + inventory_hostname
       + '/5432/credentials/paperless/password'
       + ' length=64 chars=ascii_letters,digits,.-_~&()*=') }}"

   paperless__secret_key:     "{{ lookup('password', secret
       + '/docker_compose_service/paperless/secret_key'
       + ' length=64 chars=ascii_letters,digits') }}"
   paperless__admin_password: "{{ lookup('password', secret
       + '/docker_compose_service/paperless/admin_password'
       + ' length=24 chars=ascii_letters,digits') }}"

   # API tokens of the dedicated sidecar accounts. Generated by the post_main
   # custom task and stored in the secret directory. Empty on a fresh install
   # (see "Dedicated service accounts" below). lookup('file', ...) is used
   # instead of 'password' because the value is produced inside the container,
   # not generated by Ansible.
   paperless__gpt_api_token: "{{ lookup('file', secret
       + '/docker_compose_service/paperless/gpt_api_token', errors='warn')
       | default('') }}"
   paperless__ai_api_token:  "{{ lookup('file', secret
       + '/docker_compose_service/paperless/ai_api_token', errors='warn')
       | default('') }}"

   docker_compose_service__host_services:

     - name: 'paperless'
       compose_src: 'paperless/docker-compose.yml'
       data_dirs:
         # data/ stays on local storage (Whoosh index + ML classifiers do not
         # tolerate NFS locking); media/export/consume are on an NFS mount.
         # owner/group is the local 'paperless' service account, uid/gid 800
         # (an arbitrary local convention -- see the note after this example).
         - { path: '/srv/docker/paperless/data',    owner: '800', group: '800' }
         - { path: '/mnt/paperless/media',          owner: '800', group: '800' }
         - { path: '/mnt/paperless/export',         owner: '800', group: '800' }
         - { path: '/mnt/paperless/consume',        owner: '800', group: '800' }
         - { path: '/srv/docker/paperless/paperless-gpt/prompts', owner: '800', group: '800' }
         - { path: '/srv/docker/paperless/paperless-gpt/hocr',    owner: '800', group: '800' }
         - { path: '/srv/docker/paperless/paperless-ai/data',     owner: '800', group: '800' }
       env:
         # PostgreSQL and Redis over UNIX socket from the host
         PAPERLESS_DBENGINE: 'postgresql'
         PAPERLESS_DBHOST:   '/var/run/postgresql'
         PAPERLESS_DBNAME:   'paperless'
         PAPERLESS_DBUSER:   'paperless'
         PAPERLESS_DBPASS:   '{{ paperless__postgresql_password }}'
         PAPERLESS_REDIS:    'unix:///var/run/redis/redis-server.sock'
         PAPERLESS_SECRET_KEY:     '{{ paperless__secret_key }}'
         PAPERLESS_ADMIN_USER:     'admin'
         PAPERLESS_ADMIN_PASSWORD: '{{ paperless__admin_password }}'
         PAPERLESS_URL:            'https://paperless.example.com'
         # nginx + proxy in front: trust the loopback proxy
         PAPERLESS_TRUSTED_PROXIES:    '127.0.0.1,::1'
         PAPERLESS_USE_X_FORWARD_HOST: 'true'
         PAPERLESS_USE_X_FORWARD_PORT: 'true'
         PAPERLESS_PROXY_SSL_HEADER:   '["HTTP_X_FORWARDED_PROTO", "https"]'
         USERMAP_UID: '800'
         USERMAP_GID: '800'
         # API token for the paperless-gpt sidecar (its own account, not admin)
         PAPERLESS_GPT_API_TOKEN: '{{ paperless__gpt_api_token }}'
       # Pre-seed the paperless-ai configuration (.env) so its web wizard is
       # skipped on first start. A template is used (not inline content) because
       # a long multi-line content block in host_vars trips over ansible_managed.
       config_files:
         - dest: '/srv/docker/paperless/paperless-ai/data/.env'
           owner: '800'
           group: '800'
           mode: '0600'
           src: 'paperless-ai-data.env.j2'
       nginx:
         enabled: true
         fqdn: 'paperless.example.com'
         port: '8000'
         proxy_options: |
           client_max_body_size 100M;
           proxy_read_timeout 300s;

.. note::

   ``800`` is **not** a special number. It is simply the uid/gid of a local
   ``paperless`` service account created on the host with the
   :ref:`debops.system_users` role (this homelab reserves the 800-849 range for
   Docker service accounts):

   .. code-block:: yaml

      # host_vars/paperless.example.com/system_users.yml
      system_users__host_accounts:
        - name: 'paperless'
          uid: '800'
          group: 'paperless'
          gid: '800'

   The same value is reused for the ``data_dirs`` ``owner``/``group``, for
   ``USERMAP_UID``/``USERMAP_GID`` (the paperless-ngx container drops to it) and
   for the sidecars' ``PUID``/``PGID``, so every file the containers create on
   the (possibly NFS-mounted) data directories is owned by one known, non-root
   account. Pick whatever uid/gid your environment uses; only consistency
   between the host account, the volume ownership and the in-container user
   mapping matters.

.. note::

   ``paperless__postgresql_password`` must use the same secret path and password
   parameters as the :ref:`debops.postgresql` role
   (see `PostgreSQL role and database`_ above). If they drift, the role and the
   application derive different passwords and Paperless cannot authenticate to
   the database.


Compose file template
~~~~~~~~~~~~~~~~~~~~~~

The Compose file omits the ``db`` and ``broker`` services from the upstream
example (they live on the host) and bind-mounts the host sockets. The sidecars
reach Paperless through the Compose network name ``webserver`` (not
``container_name``):

.. code-block:: yaml

   # {{ ansible_managed }}
   name: paperless

   services:

     webserver:
       container_name: paperless_webserver
       image: ghcr.io/paperless-ngx/paperless-ngx:latest
       env_file: [ .env ]
       ports:
         - '127.0.0.1:8000:8000'
       volumes:
         - /srv/docker/paperless/data:/usr/src/paperless/data
         - /mnt/paperless/media:/usr/src/paperless/media
         - /mnt/paperless/export:/usr/src/paperless/export
         - /mnt/paperless/consume:/usr/src/paperless/consume
         # PostgreSQL socket read-only (peer auth only reads); Redis socket must
         # be read-write -- connect(2) on an AF_UNIX socket needs write access.
         - /var/run/postgresql:/var/run/postgresql:ro
         - /var/run/redis:/var/run/redis
       healthcheck:
         test: ['CMD', 'curl', '-fs', '--max-time', '2', 'http://localhost:8000']
         interval: 30s
         timeout: 10s
         retries: 5
       depends_on: [ gotenberg, tika ]

     gotenberg:
       container_name: paperless_gotenberg
       image: docker.io/gotenberg/gotenberg:8
       command:
         - 'gotenberg'
         - '--chromium-disable-javascript=true'
         - '--chromium-allow-list=file:///tmp/.*'

     tika:
       container_name: paperless_tika
       image: docker.io/apache/tika:latest

     paperless-gpt:
       container_name: paperless_gpt
       image: ghcr.io/icereed/paperless-gpt:latest
       environment:
         - PAPERLESS_BASE_URL=http://webserver:8000
         - PAPERLESS_API_TOKEN=${PAPERLESS_GPT_API_TOKEN}
         - LLM_PROVIDER=ollama
         - LLM_MODEL=llama3.1
         - OLLAMA_HOST=http://ollama.example.com:11434
       ports:
         - '127.0.0.1:8080:8080'
       depends_on:
         webserver:
           condition: service_healthy

     paperless-ai:
       container_name: paperless_ai
       image: clusterzx/paperless-ai:latest
       environment:
         - PUID=800
         - PGID=800
         - RAG_SERVICE_ENABLED=true
       ports:
         - '127.0.0.1:3000:3000'
       volumes:
         - /srv/docker/paperless/paperless-ai/data:/app/data
       depends_on:
         webserver:
           condition: service_healthy

.. important::

   The Redis socket directory is mounted **read-write**
   (``/var/run/redis:/var/run/redis``). Mounting it ``:ro`` breaks the client:
   ``connect(2)`` on an ``AF_UNIX`` stream socket requires write permission on
   the socket node, so a read-only mount yields ``PermissionError [Errno 13]``
   regardless of the Redis ``unixsocketperm`` setting.


Dedicated service accounts and API tokens
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

So that the document history records which sidecar made a change, each sidecar
gets its **own** Django account and API token instead of sharing ``admin``.
The accounts and tokens are bootstrapped with the role's custom tasks (see
:ref:`Custom Ansible tasks <docker_compose_service__ref_custom_tasks>` in
*Getting started*), placed under the project's ``override_paths.tasks_path``
(by default
:file:`ansible/overrides/tasks/docker_compose_service/`).

``pre_main.yml`` -- create empty token files **before** the service list is
evaluated. Without this, the ``lookup('file', ...)`` for the not-yet-generated
tokens raises (even with ``errors='warn'``) and collapses
:envvar:`docker_compose_service__host_services` to an empty list, so nothing is
deployed:

.. code-block:: yaml

   # ansible/overrides/tasks/docker_compose_service/pre_main.yml
   ---

   - name: Bootstrap paperless sidecar API token secret files
     when: inventory_hostname == 'paperless.example.com'
     delegate_to: localhost
     become: false
     block:

       - name: Ensure paperless API token secret directory exists
         ansible.builtin.file:
           path: '{{ secret }}/docker_compose_service/paperless'
           state: 'directory'
           mode: '0700'

       - name: Ensure paperless sidecar token files exist (empty if new)
         ansible.builtin.copy:
           content: ''
           dest: '{{ secret }}/docker_compose_service/paperless/{{ item }}'
           mode: '0600'
           force: false   # never overwrite an already-generated token
         loop: [ 'gpt_api_token', 'ai_api_token' ]

``post_main.yml`` -- once the containers are up, create the accounts
(idempotently) and generate their tokens inside the ``webserver`` container,
saving each token back to the secret directory only when its file is still
empty:

.. code-block:: yaml

   # ansible/overrides/tasks/docker_compose_service/post_main.yml
   ---

   - name: Provision paperless dedicated service accounts and API tokens
     when: inventory_hostname == 'paperless.example.com'
     block:

       - name: Create paperless-gpt Django service account (idempotent)
         ansible.builtin.command:
           # 'docker exec' runs as root by default; --user paperless (uid 800)
           # is required so the in-container Django system check on the
           # NFS-owned media/consume dirs (owner 800) passes.
           argv:
             - docker
             - exec
             - '--user'
             - paperless
             - paperless_webserver
             - python
             - manage.py
             - shell
             - -c
             - >-
               from django.contrib.auth.models import User;
               User.objects.get_or_create(username='paperless-gpt',
               defaults={'is_superuser': True, 'is_staff': True, 'email': ''})
         changed_when: false

       - name: Check paperless sidecar token secret files
         ansible.builtin.stat:
           path: '{{ secret }}/docker_compose_service/paperless/{{ item }}'
         register: paperless__stat_tokens
         loop: [ 'gpt_api_token', 'ai_api_token' ]
         delegate_to: localhost
         become: false

       - name: Generate paperless-gpt API token
         ansible.builtin.command:
           argv:
             - docker
             - exec
             - '--user'
             - paperless
             - paperless_webserver
             - python
             - manage.py
             - drf_create_token
             - paperless-gpt
         register: paperless__register_gpt_token
         changed_when: false
         when: paperless__stat_tokens.results[0].stat.size == 0

       - name: Save paperless-gpt API token to the secret store
         ansible.builtin.copy:
           content: '{{ paperless__register_gpt_token.stdout.split()[2] }}'
           dest: '{{ secret }}/docker_compose_service/paperless/gpt_api_token'
           mode: '0600'
         delegate_to: localhost
         become: false
         when:
           - paperless__stat_tokens.results[0].stat.size == 0
           - paperless__register_gpt_token is not skipped
           - paperless__register_gpt_token is succeeded

   # The paperless-ai account and token follow the same pattern.

.. note::

   The custom tasks run for **every** host in
   ``[debops_service_docker_compose_service]``, so each block is guarded with
   ``when: inventory_hostname == '...'``.


Two-pass convergence
~~~~~~~~~~~~~~~~~~~~~

On a **fresh install** the tokens do not exist yet, so the order of operations
spans two role runs:

1. ``pre_main`` creates empty token files -> the ``lookup('file', ...)`` returns
   an empty string -> the ``.env`` files render with empty tokens -> the
   containers start (the sidecars cannot authenticate yet).
2. ``post_main`` creates the Django accounts and writes the real tokens to the
   secret directory.
3. Re-running ``debops run service/docker_compose_service`` re-reads the now
   populated token files, regenerates the ``.env`` files and recreates the
   sidecars with valid tokens.

This second pass is expected; it is the same convergence pattern used for any
value that is produced by the application itself rather than by Ansible.


LAN-only sidecar UIs
~~~~~~~~~~~~~~~~~~~~~

The sidecars bind to loopback (``127.0.0.1:8080`` and ``127.0.0.1:3000``).
Their web UIs are published on separate :command:`nginx` virtual hosts
restricted to the LAN, configured in a host-level
:file:`host_vars/.../nginx.yml` (not through the service's ``nginx:`` block,
which is reserved for the main application):

.. code-block:: yaml

   # host_vars/paperless.example.com/nginx.yml
   nginx__servers:
     - name: [ 'paperless-gpt.example.com' ]
       filename: 'paperless-gpt.example.com'
       location_list:
         - pattern: '/'
           options: |
             proxy_pass http://127.0.0.1:8080;
       allow: [ '10.0.0.0/8' ]
       deny_all: true

Add the sidecar FQDNs to the host's PKI realm
(:file:`host_vars/.../pki.yml`) so the certificate covers them as Subject
Alternative Names.


.. _docker_compose_service__guide_ollama:

Ollama API with LAN firewall (DOCKER-USER)
------------------------------------------

`Ollama <https://ollama.com/>`_ is a local LLM inference server. It publishes
a REST API on port ``11434`` that other hosts on the same network can consume.
Rather than exposing the port openly, this example restricts access to the SRV
VLAN and explains why ``DOCKER-USER`` — not ``INPUT`` — is the correct chain.


Why ``INPUT`` does not work
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker-published ports use DNAT: incoming packets are rewritten in
``nat/PREROUTING`` and then travel through the ``FORWARD`` chain, where
Docker's own rules accept them. They **never reach the** ``INPUT`` **chain**.
An ``iptables`` rule in ``INPUT`` such as::

    -A INPUT -p tcp --dport 11434 -j REJECT

appears correct and passes review, but has zero effect on published container
traffic. The correct location is ``DOCKER-USER``, which is inserted at the
**top** of the ``FORWARD`` chain by Docker specifically for user-defined rules.


Inventory
~~~~~~~~~

.. code-block:: none

   [debops_service_docker_server]
   srv.example.com

   [debops_service_docker_compose_service]
   srv.example.com


Service definition
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # ansible/inventory/host_vars/srv.example.com/docker_compose_service.yml
   ---

   docker_compose_service__host_services:

     - name: 'ollama'
       compose_src: 'ollama/docker-compose.yml'
       published_ports:
         - port: 11434
           protocol: 'tcp'
           allow: [ '10.254.250.0/24' ]
           comment: 'Ollama API - SRV VLAN only'

The role will emit two :command:`ferm` rules into ``DOCKER-USER`` for port
``11434/tcp``:

1. ``ACCEPT`` for source ``10.254.250.0/24``
2. ``REJECT`` (default) for all other sources

Both rules are placed in a single rule file ordered before Docker's own
``RETURN`` terminator in ``DOCKER-USER``.


Compose file
~~~~~~~~~~~~

Place the template at:

.. code-block:: none

   ansible/docker_compose_service/by-host/srv.example.com/
     ollama/docker-compose.yml

.. code-block:: yaml

   # {{ ansible_managed }}
   name: ollama

   services:
     ollama:
       image: ollama/ollama:latest
       ports:
         - '11434:11434'
       volumes:
         - ollama_data:/root/.ollama
       restart: unless-stopped

   volumes:
     ollama_data:

Note that the port is bound to ``0.0.0.0`` (all interfaces), so it is
reachable from the LAN. The ``published_ports`` firewall entry restricts
access to the SRV VLAN only.


Verification
~~~~~~~~~~~~

After running the playbook, verify the rules are in place:

.. code-block:: console

   $ iptables -L DOCKER-USER -n -v --line-numbers

The output should include:

.. code-block:: none

   Chain DOCKER-USER (1 references)
   num  target  prot opt source            destination
   1    ACCEPT  tcp  --  10.254.250.0/24   0.0.0.0/0    tcp dpt:11434
   2    REJECT  tcp  --  0.0.0.0/0         0.0.0.0/0    tcp dpt:11434 reject-with icmp-admin-prohibited
   3    RETURN  all  --  0.0.0.0/0         0.0.0.0/0

.. important::

   Rules **1** and **2** must appear **above** the ``RETURN`` terminator (rule
   **3**). If they appear after ``RETURN``, they are dead rules that will never
   be evaluated. The role's generated rules are applied via :command:`ferm`
   which manages the complete ``DOCKER-USER`` chain, so ordering is correct by
   default.

Test from a host inside the allowed VLAN:

.. code-block:: console

   $ curl http://srv.example.com:11434/

Test from a host **outside** the allowed VLAN (should be rejected):

.. code-block:: console

   $ curl --connect-timeout 5 http://srv.example.com:11434/
   # Expected: connection refused (REJECT) or timeout (DROP)


Rule persistence after Docker restart
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :ref:`debops.docker_server` role installs a :command:`ferm` post-hook
(``/etc/ferm/hooks/post.d/restart-docker``, controlled by
:envvar:`docker_server__ferm_post_hook`) that restarts Docker after every
:command:`ferm` reload. This ensures Docker's ``FORWARD`` jumps are always
present after :command:`ferm` rebuilds the ``filter`` table.

In the other direction: when Docker itself restarts (package upgrade,
``daemon.json`` change, manual ``systemctl restart docker``), it only
**ensures the existence** of the ``DOCKER-USER`` chain — it does **not** flush
its contents. Rules placed there by :command:`ferm` therefore survive a Docker
restart.

If rules ever disappear (e.g. after a kernel module reload that drops all
iptables state), re-running ``debops run service/docker_compose_service`` will
restore them.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
