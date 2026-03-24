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
       compose_src: 'docker_compose_service/immich/docker-compose.yml'
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

   ansible/resources/templates/by-host/immich.example.com/
     docker_compose_service/immich/docker-compose.yml

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

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
