.. Copyright (C) 2025 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2025 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _cloudflared__ref_guide_docker:

Integration with Docker services
=================================

.. only:: html

   .. contents::
      :local:


Overview
--------

cloudflared can expose Docker containers managed by ``debops.docker_service``
or ``debops.docker_compose_service`` to the internet through Cloudflare
Tunnel. There are two main approaches:

**Direct routing** -- cloudflared ingress points directly to the container's
published port on the host. Simplest setup, best for single-container services.

**Through nginx** -- cloudflared routes to nginx, which acts as a reverse proxy
to the container. Provides full control over TLS, headers, caching, and
virtual host routing. Best for multi-container setups or when you need
nginx features.

.. code-block:: text

   Approach 1: Direct

   Cloudflare Edge --> cloudflared --> container (host port)

   Approach 2: Through nginx

   Cloudflare Edge --> cloudflared --> nginx --> container (host port)


Direct routing to Docker containers
------------------------------------

When a Docker container publishes a port on the host (e.g., ``3000:3000``),
cloudflared can route traffic directly to it.

Example with ``debops.docker_service``:

.. code-block:: yaml

   # Container definition (docker_service role)
   docker_service__host_services:
     - name: 'gitea'
       image: 'gitea/gitea:latest'
       ports:
         - '127.0.0.1:3000:3000'
       volumes:
         - '/srv/docker/gitea/data:/data'

   # Cloudflared tunnel configuration
   cloudflared__host_tunnels:
     - name: 'docker-apps'
       mode: 'local'
       tunnel_uuid: 'abc12345-...'
       ingress:
         - hostname: 'gitea.example.com'
           service: 'http://127.0.0.1:3000'

Example with ``debops.docker_compose_service``:

.. code-block:: yaml

   # Docker Compose project definition
   docker_compose_service__host_services:
     - name: 'monitoring'
       compose_content:
         services:
           grafana:
             image: 'grafana/grafana:latest'
             ports:
               - '127.0.0.1:3100:3000'
           prometheus:
             image: 'prom/prometheus:latest'
             ports:
               - '127.0.0.1:9090:9090'

   # Cloudflared tunnel configuration
   cloudflared__host_tunnels:
     - name: 'monitoring'
       mode: 'local'
       tunnel_uuid: 'def67890-...'
       ingress:
         - hostname: 'grafana.example.com'
           service: 'http://127.0.0.1:3100'
         - hostname: 'prometheus.example.com'
           service: 'http://127.0.0.1:9090'

.. note::

   Bind container ports to ``127.0.0.1`` instead of ``0.0.0.0`` when using
   cloudflared, since direct internet access is not needed and this prevents
   accidental exposure.


Routing through nginx
---------------------

For more complex setups, route cloudflared traffic through nginx. This is
especially useful when:

- You need WebSocket support with specific nginx tuning
- You want nginx-level caching or rate limiting
- Multiple containers share a hostname with different paths
- You need custom headers or rewrites

.. code-block:: yaml

   # Container definition
   docker_service__host_services:
     - name: 'webapp'
       image: 'myapp:latest'
       ports:
         - '127.0.0.1:8080:8080'

   # nginx configuration (via debops.nginx or docker_service nginx integration)
   nginx__servers:
     - name: 'webapp.example.com'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8080'
       proxy_options: |
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "upgrade";

   # Cloudflared: all traffic goes through nginx
   cloudflared__host_tunnels:
     - name: 'web'
       mode: 'local'
       tunnel_uuid: 'abc12345-...'
       ingress:
         - hostname: 'webapp.example.com'
           service: 'http://127.0.0.1:80'

The ``docker_service`` and ``docker_compose_service`` roles have built-in nginx
integration via dependent variables (``*__nginx__dependent_upstreams`` and
``*__nginx__dependent_servers``). When using these, nginx is automatically
configured as a reverse proxy for the containers.


Token mode with Cloudflare dashboard
-------------------------------------

The simplest approach is to use token mode and configure routing in the
Cloudflare dashboard:

.. code-block:: yaml

   # Just run cloudflared with a token
   cloudflared__host_tunnels:
     - name: 'apps'

   # Containers publish ports on localhost
   docker_service__host_services:
     - name: 'gitea'
       image: 'gitea/gitea:latest'
       ports:
         - '127.0.0.1:3000:3000'

     - name: 'nextcloud'
       image: 'nextcloud:latest'
       ports:
         - '127.0.0.1:8080:80'

Then in the Cloudflare Zero Trust dashboard, configure public hostnames:

- ``gitea.example.com`` -> ``http://localhost:3000``
- ``cloud.example.com`` -> ``http://localhost:8080``


Complete example: multi-service host
-------------------------------------

A complete example combining cloudflared, nginx, and Docker on a single host:

.. code-block:: yaml

   # host_vars/server/cloudflared.yml
   cloudflared__host_tunnels:
     - name: 'services'
       mode: 'local'
       tunnel_uuid: 'abc12345-6789-def0-1234-56789abcdef0'
       config:
         protocol: 'quic'
         metrics: '127.0.0.1:2000'
       ingress:
         # Web apps through nginx
         - hostname: 'app.example.com'
           service: 'http://127.0.0.1:80'
         - hostname: 'cloud.example.com'
           service: 'http://127.0.0.1:80'
         # Direct to container
         - hostname: 'gitea.example.com'
           service: 'http://127.0.0.1:3000'
         # Non-HTTP service
         - hostname: 'ssh.example.com'
           service: 'ssh://127.0.0.1:22'

   # host_vars/server/docker_service.yml
   docker_service__host_services:
     - name: 'webapp'
       image: 'myapp:latest'
       ports:
         - '127.0.0.1:8080:8080'

     - name: 'gitea'
       image: 'gitea/gitea:latest'
       ports:
         - '127.0.0.1:3000:3000'

     - name: 'nextcloud'
       image: 'nextcloud:latest'
       ports:
         - '127.0.0.1:8081:80'

   # host_vars/server/nginx.yml
   nginx__servers:
     - name: 'app.example.com'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8080'

     - name: 'cloud.example.com'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8081'
       proxy_options: |
         client_max_body_size 512m;
