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
3. nginx receives the request on the loopback interface and routes it based
   on ``Host`` header to the appropriate backend.

.. code-block:: text

   Internet client
       |
       v
   Cloudflare Edge (TLS termination, WAF, DDoS protection)
       |
       v (encrypted tunnel)
   cloudflared (localhost)
       |
       v (HTTPS to 127.0.0.1:443)
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


HTTP to HTTPS redirects
-----------------------

When the :ref:`debops.pki` role manages certificates on the host,
:ref:`debops.nginx` configures each server to redirect HTTP requests on
port ``80`` to HTTPS. If cloudflared sends requests to
``http://127.0.0.1:80``, nginx answers with a redirect to the same
``https://`` URL the client has already used, the client follows it to the
Cloudflare edge, the request reaches port ``80`` again and the browser
stops with a "too many redirects" error.

Point cloudflared to the HTTPS port of nginx instead, as shown in the
examples below. cloudflared verifies the nginx certificate using the
system certificate store, which should trust the CA that issued it (for
example the internal CA of a :ref:`debops.pki` realm); the
``originServerName`` parameter selects the server name used for SNI and
certificate verification.

If nginx should accept plain HTTP from cloudflared, disable the redirect
for the relevant servers with the ``redirect_to_ssl: False`` parameter of
:ref:`debops.nginx`. The server will then also be available over plain
HTTP on all interfaces it listens on.


Token mode
----------

When using token mode, the ingress/routing rules are managed in the Cloudflare
dashboard. Cloudflared just needs to run and connect.

Ansible inventory:

.. code-block:: yaml

   # host_vars/webserver/cloudflared.yml
   cloudflared__tunnels:
     - name: 'web'

Place the token at ``secret/cloudflared/tunnels/web/token``.

Then in the Cloudflare Zero Trust dashboard, add public hostnames for the
tunnel, each pointing to ``https://localhost:443`` with the "Origin Server
Name" option in the TLS settings set to the public hostname:

- ``app.example.com`` -> ``https://localhost:443``
- ``api.example.com`` -> ``https://localhost:443``

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
       config:
         ingress:
           - hostname: 'app.example.com'
             service: 'https://127.0.0.1:443'
             originRequest:
               originServerName: 'app.example.com'
           - hostname: 'api.example.com'
             service: 'https://127.0.0.1:443'
             originRequest:
               originServerName: 'api.example.com'

All hostnames point to the same nginx port. nginx is then configured with
separate ``server`` blocks (managed by :ref:`debops.nginx`) to route to
different backends:

.. code-block:: yaml

   # host_vars/webserver/nginx.yml
   nginx__servers:
     - name: 'app.example.com'
       filename: 'app.example.com'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8080'

     - name: 'api.example.com'
       filename: 'api.example.com'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8081'


Client IP addresses
-------------------

All requests delivered by cloudflared come from ``127.0.0.1``. Without
additional configuration nginx logs this address for every client, rate
limits apply to all clients together, and IP-based access lists (for
example the ``allow`` parameter of :ref:`debops.nginx` servers) either
block the tunnel or allow every client, depending on whether the loopback
address is allowed.

Cloudflare passes the original client address in the ``CF-Connecting-IP``
header, which can be used by the nginx ``realip`` module:

.. code-block:: yaml

   nginx__servers:
     - name: 'app.example.com'
       type: 'proxy'
       proxy_pass: 'http://127.0.0.1:8080'
       options: |
         set_real_ip_from 127.0.0.1;
         real_ip_header CF-Connecting-IP;

The ``set_real_ip_from`` directive trusts the header in every connection
from the loopback address, not only in connections made by cloudflared.
Any local process, including containers that use the host network, can
connect to nginx and set ``CF-Connecting-IP`` to an arbitrary address,
which then shows up in the logs and is used by rate limits and IP-based
access lists. Use the restored address only on hosts where all local
processes are trusted, and restrict access to the tunnelled services with
Cloudflare Access policies rather than with nginx access lists.


Mixed services
--------------

cloudflared can route non-HTTP protocols directly (without nginx) while
HTTP traffic goes through nginx:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'mixed'
       mode: 'local'
       tunnel_uuid: 'abc12345-6789-def0-1234-56789abcdef0'
       config:
         ingress:
           - hostname: 'www.example.com'
             service: 'https://127.0.0.1:443'
             originRequest:
               originServerName: 'www.example.com'
           - hostname: 'ssh.example.com'
             service: 'ssh://127.0.0.1:22'
           - hostname: 'db.example.com'
             service: 'tcp://127.0.0.1:5432'

In this example, HTTP traffic goes through nginx while SSH and PostgreSQL
traffic is routed directly to the respective daemons.

SSH and TCP hostnames are reached with a Cloudflare Access client, not
by opening the origin port. For SSH, use :command:`cloudflared` as the
``ProxyCommand`` in the client's :file:`~/.ssh/config`:

.. code-block:: none

   Host ssh.example.com
     ProxyCommand cloudflared access ssh --hostname %h

Then connect with the usual SSH client:

.. code-block:: console

   $ ssh user@ssh.example.com

For other TCP services, start a local listener that forwards connections
through the tunnel on a free local port, then point the client at that
port (here :command:`psql` connects to the remote PostgreSQL server):

.. code-block:: console

   $ cloudflared access tcp --hostname db.example.com --url localhost:15432
   $ psql --host localhost --port 15432 --username dbuser dbname

Create an Access application and policy for each hostname if the tunnel
is reachable outside a trusted network.


Certificate verification
------------------------

If the nginx certificate is not trusted by the host, for example because
it is self-signed, cloudflared refuses the connection. The
``noTLSVerify: True`` origin parameter disables certificate validation:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'secure'
       mode: 'local'
       tunnel_uuid: 'abc12345-6789-def0-1234-56789abcdef0'
       config:
         originRequest:
           noTLSVerify: True
         ingress:
           - hostname: 'secure.example.com'
             service: 'https://127.0.0.1:443'

The loopback connection is still encrypted, but cloudflared does not
authenticate nginx. Treat this as an exception, not a secure default, and
prefer a certificate issued by :ref:`debops.pki`.
