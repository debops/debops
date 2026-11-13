.. Copyright (C) 2025 Patryk Ściborek <patryk@sciborek.com>
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
:envvar:`cloudflared__combined_tunnels` and processed in order. Entries with
the same ``name`` are merged together, so a tunnel defined for a group of
hosts can be changed or removed on a specific host. Parameters of a later
entry replace the parameters of an earlier one; the ``config`` dictionary
is replaced as a whole.

Each list entry is a dictionary with the following supported parameters:

``name``
  Required. The name of the tunnel instance. Used as the systemd instance
  identifier (``cloudflared@<name>.service``), as the base name for
  configuration and secret files (``<name>.yml``, ``<name>.token``,
  ``<name>.json``) and as the name of the directory with the tunnel secrets.

``state``
  Optional, default: ``present``. If ``absent``, the tunnel instance will be
  stopped, disabled and its configuration files removed. If ``init``, the
  tunnel is defined but not managed, which can be used to prepare a tunnel
  that is activated later with ``state: 'present'``. If ``ignore``, the
  entry is not evaluated by the role.

``mode``
  Optional, default: ``token``. The tunnel management mode:

  ``token``
    The tunnel is managed remotely via the Cloudflare dashboard. The token is
    read from the secret store at
    ``secret/cloudflared/tunnels/<name>/token``.

  ``local``
    The tunnel configuration, including ingress rules, is managed locally.
    Credentials JSON is read from the secret store at
    ``secret/cloudflared/tunnels/<name>/credentials.json``.

  The role checks that the secret file exists on the Ansible Controller
  before the tunnel is configured.

``tunnel_uuid``
  Required when ``mode`` is ``local``. The UUID of the tunnel, obtained from
  ``cloudflared tunnel create`` or the Cloudflare dashboard.

``config``
  Optional. A YAML dictionary with the :command:`cloudflared` configuration
  of the tunnel. It is merged recursively with
  :envvar:`cloudflared__default_config` and :envvar:`cloudflared__config`
  and written to the tunnel configuration file as is, so the keys use the
  names from the `cloudflared documentation`__, for example:

  - ``protocol`` -- connection protocol (``auto``, ``http2``, ``quic``)
  - ``loglevel`` -- log verbosity (``debug``, ``info``, ``warn``,
    ``error``, ``fatal``)
  - ``metrics`` -- address of the Prometheus metrics endpoint
  - ``edge-ip-version`` -- IP version used to connect to the Cloudflare
    edge (``auto``, ``4``, ``6``)
  - ``retries``, ``grace-period``, ``post-quantum``
  - ``logfile`` -- path of the log file, for example in
    :envvar:`cloudflared__log_dir`
  - ``originRequest`` -- default origin parameters for all ingress rules,
    for example ``connectTimeout``, ``noTLSVerify``, ``originServerName``,
    ``httpHostHeader`` or ``access``
  - ``warp-routing`` -- parameters of the private network routing:
    ``connectTimeout``, ``maxActiveFlows``, ``tcpKeepAlive``
  - ``ingress`` -- list of ingress rules, used in the ``local`` mode

  In the ``local`` mode the role adds the ``tunnel`` and
  ``credentials-file`` options. Each ingress rule supports the
  ``hostname``, ``path``, ``service`` and ``originRequest`` keys; the
  ``service`` key can point to an HTTP or HTTPS origin
  (``http://127.0.0.1:80``), a TCP or SSH origin (``tcp://127.0.0.1:5432``,
  ``ssh://127.0.0.1:22``), a UNIX socket (``unix:/path/to/socket``), the
  built-in ``hello_world`` server or a static ``http_status:NNN`` response.
  :command:`cloudflared` requires the last rule to match all requests; if
  the last rule has a ``hostname`` or ``path``, the role appends a rule with
  the service from the ``catch_all_service`` parameter.

  In the ``token`` mode the role adds the ``token-file`` option. The ingress
  rules are managed in the Cloudflare dashboard and the ``ingress`` key is
  ignored by :command:`cloudflared`.

  .. __: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/configure-tunnels/local-management/configuration-file/

``catch_all_service``
  Optional. The service of the catch-all ingress rule added by the role in
  the ``local`` mode. Default: :envvar:`cloudflared__catch_all_service`
  (``http_status:404``).


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
         post-quantum: True
         originRequest:
           connectTimeout: '30s'
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

**Private network tunnel**:

Private network routing is enabled per tunnel in the Cloudflare dashboard or
with the ``cloudflared tunnel route ip add`` command; the ``warp-routing``
section only tunes its parameters:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'private-network'
       mode: 'local'
       tunnel_uuid: 'abc12345-6789-def0-1234-56789abcdef0'
       config:
         warp-routing:
           connectTimeout: '10s'
           maxActiveFlows: 1000

The :command:`cloudflared` daemon runs as an unprivileged user. To proxy
ICMP traffic of the private network, the primary group of that user needs
to be included in the ``net.ipv4.ping_group_range`` kernel parameter, which
can be set using the :ref:`debops.sysctl` role.

**Multiple tunnels on one host**:

.. code-block:: yaml

   cloudflared__host_tunnels:
     - name: 'web-tunnel'
       mode: 'token'
       config:
         metrics: '127.0.0.1:20241'

     - name: 'internal-tunnel'
       mode: 'local'
       tunnel_uuid: 'deadbeef-1234-5678-9abc-def012345678'
       config:
         metrics: '127.0.0.1:20242'
         ingress:
           - hostname: 'internal.example.com'
             service: 'http://127.0.0.1:8080'

Each tunnel needs its own metrics address. Without the ``metrics`` option
each tunnel picks the first free port from the ``20241`` - ``20245`` range
on ``localhost``, which works as well but does not guarantee which tunnel
uses which port.

**Removing a tunnel**:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'old-tunnel'
       state: 'absent'
