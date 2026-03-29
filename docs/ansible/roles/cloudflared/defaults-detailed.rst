.. Copyright (C) 2025 Marcin Sciborski <marcin@sciborski.com>
.. Copyright (C) 2025 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _cloudflared__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.cloudflared`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation
and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _cloudflared__ref_tunnels:

cloudflared__tunnels
--------------------

The ``cloudflared__default_tunnels``, ``cloudflared__tunnels``,
``cloudflared__group_tunnels``, ``cloudflared__host_tunnels`` lists define
Cloudflare Tunnel instances managed by the role. They are combined into
:envvar:`cloudflared__combined_tunnels` and processed in order.

Each list entry is a dictionary with the following supported parameters:

``name``
  Required. The name of the tunnel instance. Used as the systemd instance
  identifier (``cloudflared@<name>.service``) and as the base name for
  configuration files (``<name>.yml``, ``<name>.env``, ``<name>.json``).

``state``
  Optional, default: ``present``. If ``absent``, the tunnel instance will be
  stopped, disabled and its configuration files removed.

``mode``
  Optional, default: ``token``. The tunnel management mode:

  ``token``
    The tunnel is managed remotely via the Cloudflare dashboard. The token is
    read from the secret store at
    ``secret/cloudflared/tunnels/<name>/token``.

  ``local``
    The tunnel configuration (ingress rules, origin parameters, WARP routing)
    is managed locally. Credentials JSON is read from the secret store at
    ``secret/cloudflared/tunnels/<name>/credentials.json``.

``tunnel_uuid``
  Required when ``mode`` is ``local``. The UUID of the tunnel, obtained from
  ``cloudflared tunnel create`` or the Cloudflare dashboard.

``config``
  Optional. A dictionary of cloudflared configuration options that will be
  written directly to the tunnel's YAML config file. These override the
  global defaults. Supported keys include:

  - ``protocol`` -- Connection protocol (``auto``, ``http2``, ``quic``)
  - ``loglevel`` -- Log verbosity (``debug``, ``info``, ``warn``, ``error``, ``fatal``)
  - ``metrics`` -- Prometheus metrics endpoint (e.g., ``127.0.0.1:2000``)
  - ``no-autoupdate`` -- Disable auto-update (boolean)
  - ``post-quantum`` -- Enable post-quantum cryptography (boolean)
  - ``edge-ip-version`` -- IP version for edge connection (``auto``, ``4``, ``6``)
  - ``retries`` -- Connection retry count (integer)
  - ``grace-period`` -- Shutdown grace period (e.g., ``30s``)
  - ``tag`` -- Custom tags (dictionary)

``ingress``
  Optional (used with ``mode: local``). A list of ingress rule dictionaries.
  Each rule can have:

  ``hostname``
    The hostname to match (supports wildcards like ``*.example.com``).

  ``path``
    Optional. A regex path to match (Go regex syntax).

  ``service``
    Required. The origin service URL. Supported formats:

    - ``http://127.0.0.1:80`` -- HTTP origin
    - ``https://127.0.0.1:443`` -- HTTPS origin
    - ``tcp://127.0.0.1:22`` -- TCP origin (SSH, databases, etc.)
    - ``ssh://127.0.0.1:22`` -- SSH origin
    - ``unix:/path/to/socket`` -- Unix socket origin
    - ``hello_world`` -- Built-in test server
    - ``http_status:NNN`` -- Static HTTP status code

  ``originRequest``
    Optional. Per-rule origin request overrides (see ``origin_request`` below).

  The role automatically appends a mandatory catch-all rule at the end.

``catch_all_service``
  Optional. Override the default catch-all service for the last ingress rule.
  Default: :envvar:`cloudflared__catch_all_service` (``http_status:404``).

``origin_request``
  Optional. A dictionary of global origin request settings for the tunnel.
  Applied to all ingress rules unless overridden per-rule. Supported keys:

  - ``connectTimeout`` -- Timeout for connecting to origin (e.g., ``30s``)
  - ``tlsTimeout`` -- TLS handshake timeout (e.g., ``10s``)
  - ``tcpKeepAlive`` -- TCP keepalive interval (e.g., ``30s``)
  - ``noHappyEyeballs`` -- Disable Happy Eyeballs (boolean)
  - ``keepAliveConnections`` -- Max idle connections (integer)
  - ``keepAliveTimeout`` -- Idle connection timeout (e.g., ``90s``)
  - ``httpHostHeader`` -- Override Host header
  - ``originServerName`` -- TLS SNI server name
  - ``noTLSVerify`` -- Skip TLS verification (boolean)
  - ``disableChunkedEncoding`` -- Disable chunked encoding (boolean)
  - ``proxyAddress`` -- Proxy bind address (e.g., ``127.0.0.1``)
  - ``proxyPort`` -- Proxy port (integer)
  - ``proxyType`` -- Proxy type (e.g., ``""`` or ``"socks"``)
  - ``http2Origin`` -- Use HTTP/2 to origin (boolean)
  - ``access`` -- Access policy settings (dictionary with ``required``, ``teamName``, ``audTag``)
  - ``bastionMode`` -- Enable bastion mode (boolean)

``warp_routing``
  Optional. A dictionary to enable private network routing via Cloudflare WARP.
  Typically: ``{ enabled: true }``. When enabled, ingress rules are usually
  not needed as routing is done via WARP client.

``logfile``
  Optional. Path to a log file for this tunnel. Overrides the default log
  configuration.


Examples
~~~~~~~~

**Single token-mode tunnel** (remotely managed):

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'production'

Token stored at ``secret/cloudflared/tunnels/production/token``.

**Local tunnel with multiple ingress rules**:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'web-services'
       mode: 'local'
       tunnel_uuid: '6ff42ae2-765d-4adf-8112-31c55c1551ef'
       config:
         protocol: 'quic'
         metrics: '127.0.0.1:2000'
         post-quantum: true
       origin_request:
         connectTimeout: '30s'
         noTLSVerify: false
       ingress:
         - hostname: 'app.example.com'
           service: 'http://127.0.0.1:80'
         - hostname: 'api.example.com'
           service: 'http://127.0.0.1:8080'
           originRequest:
             httpHostHeader: 'api.internal'
         - hostname: 'ssh.example.com'
           service: 'ssh://127.0.0.1:22'

Credentials stored at
``secret/cloudflared/tunnels/web-services/credentials.json``.

**WARP private network tunnel**:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'private-network'
       mode: 'local'
       tunnel_uuid: 'abc12345-6789-def0-1234-56789abcdef0'
       warp_routing:
         enabled: true
       config:
         protocol: 'quic'
         post-quantum: true

**Multiple tunnels on one host**:

.. code-block:: yaml

   cloudflared__host_tunnels:
     - name: 'web-tunnel'
       mode: 'token'

     - name: 'internal-tunnel'
       mode: 'local'
       tunnel_uuid: 'deadbeef-1234-5678-9abc-def012345678'
       ingress:
         - hostname: 'internal.example.com'
           service: 'http://127.0.0.1:8080'

**Removing a tunnel**:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'old-tunnel'
       state: 'absent'
