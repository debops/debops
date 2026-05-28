.. Copyright (C) 2025 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2025 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _cloudflared__ref_guide_nginx:

Integration with nginx
======================

.. only:: html

   .. contents::
      :local:


Overview
--------

A common deployment pattern is to combine cloudflared with a local nginx
reverse proxy. In this setup:

1. The Cloudflare edge terminates TLS from the internet client.
2. The cloudflared tunnel delivers the request to the local server.
3. nginx receives the request on ``127.0.0.1`` and routes it based on
   ``Host`` header to the appropriate backend.

.. code-block:: text

   Internet client
       |
       v
   Cloudflare Edge (TLS termination, WAF, DDoS protection)
       |
       v (encrypted tunnel)
   cloudflared (localhost)
       |
       v (HTTP to 127.0.0.1:80)
   nginx (virtual hosts)
       |
       +---> backend app A (port 8080)
       +---> backend app B (port 8081)
       +---> static files

This is the recommended architecture when you need:

- Multiple virtual hosts behind a single tunnel
- nginx features like rate limiting, caching, rewrites, WebSocket proxying
- TLS between nginx and backend applications
- Integration with the DebOps :ref:`debops.nginx` role


Token mode (recommended)
------------------------

When using token mode, the ingress/routing rules are managed in the Cloudflare
dashboard. Cloudflared just needs to run and connect. On the Cloudflare side,
configure public hostnames pointing to ``http://localhost:80`` (or whichever
port nginx listens on).

Ansible inventory:

.. code-block:: yaml

   # host_vars/webserver/cloudflared.yml
   cloudflared__tunnels:
     - name: 'web'

Place the token at ``secret/cloudflared/tunnels/web/token``.

Then in the Cloudflare Zero Trust dashboard, add public hostnames for the
tunnel:

- ``app.example.com`` -> ``http://localhost:80``
- ``api.example.com`` -> ``http://localhost:80``

nginx will differentiate based on the ``Host`` header.


Local mode with ingress
-----------------------

When using local mode, the ingress rules are defined in the Ansible inventory:

.. code-block:: yaml

   # host_vars/webserver/cloudflared.yml
   cloudflared__tunnels:
     - name: 'web'
       mode: 'local'
       tunnel_uuid: '6ff42ae2-765d-4adf-8112-31c55c1551ef'
       ingress:
         - hostname: 'app.example.com'
           service: 'http://127.0.0.1:80'
         - hostname: 'api.example.com'
           service: 'http://127.0.0.1:80'
         - hostname: 'static.example.com'
           service: 'http://127.0.0.1:80'

All hostnames point to the same nginx port. nginx is then configured with
separate ``server`` blocks (managed by :ref:`debops.nginx`) to route to
different backends:

.. code-block:: yaml

   # host_vars/webserver/nginx.yml
   nginx__servers:
     - name: 'app.example.com'
       filename: 'app.example.com'
       by_role: 'cloudflared'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8080'

     - name: 'api.example.com'
       filename: 'api.example.com'
       by_role: 'cloudflared'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8081'


Mixed services
--------------

cloudflared can route non-HTTP protocols directly (without nginx) while
HTTP traffic goes through nginx:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'mixed'
       mode: 'local'
       tunnel_uuid: 'abc12345-...'
       ingress:
         - hostname: 'www.example.com'
           service: 'http://127.0.0.1:80'
         - hostname: 'ssh.example.com'
           service: 'ssh://127.0.0.1:22'
         - hostname: 'db.example.com'
           service: 'tcp://127.0.0.1:5432'

In this example, HTTP traffic goes through nginx while SSH and PostgreSQL
traffic is routed directly to the respective daemons.


TLS between cloudflared and nginx
----------------------------------

By default, HTTP (unencrypted) traffic between cloudflared and nginx on
``127.0.0.1`` is acceptable because it never leaves the loopback interface.
If you require encryption on the loopback (e.g., compliance requirements),
you can configure nginx to listen with TLS and point cloudflared to HTTPS:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'secure'
       mode: 'local'
       tunnel_uuid: 'abc12345-...'
       origin_request:
         noTLSVerify: true
       ingress:
         - hostname: 'secure.example.com'
           service: 'https://127.0.0.1:443'

Note: ``noTLSVerify: true`` is needed if nginx uses a self-signed certificate.
For production, consider using the :ref:`debops.pki` role to manage origin
certificates.
