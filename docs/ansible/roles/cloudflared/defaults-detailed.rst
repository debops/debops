.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
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
entry replace the parameters of an earlier one, except for the
``configuration`` list, whose entries are merged by their names, so a host
can change or remove a single option of a tunnel defined for its group.

Each list entry is a dictionary with the following supported parameters:

``name``
  Required. The name of the tunnel instance. Used as the systemd instance
  identifier (``cloudflared@<name>.service``), as the base name for
  configuration and secret files (``<name>.yml``, ``<name>.token``,
  ``<name>.json``) and as the name of the directory with the tunnel secrets.
  The name can contain letters, digits, ``.``, ``_`` and ``-``, and has to
  start with a letter or a digit.

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

``configuration``
  Optional. A list of :command:`cloudflared` configuration options of the
  tunnel, in the format described in :ref:`cloudflared__ref_configuration`.
  The entries are processed after the
  :envvar:`cloudflared__combined_configuration` list, so they can change or
  remove options set for all tunnels. In the ``local`` mode the ingress
  rules of the tunnel are set here with the ``ingress`` option.

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
       configuration:

         - name: 'protocol'
           config:
             protocol: 'quic'
             post-quantum: True

         - name: 'originRequest'
           config:
             originRequest:
               connectTimeout: '30s'

         - name: 'ingress'
           config:
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
       configuration:

         - name: 'warp-routing'
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
       configuration:

         - name: 'metrics'
           config:
             metrics: '127.0.0.1:20241'

     - name: 'internal-tunnel'
       mode: 'local'
       tunnel_uuid: 'deadbeef-1234-5678-9abc-def012345678'
       configuration:

         - name: 'metrics'
           config:
             metrics: '127.0.0.1:20242'

         - name: 'ingress'
           config:
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


.. _cloudflared__ref_configuration:

cloudflared__configuration
--------------------------

The ``cloudflared__*_configuration`` variables and the ``configuration``
parameter of each tunnel define the contents of the tunnel configuration
files in :envvar:`cloudflared__config_dir`. The role uses the
:ref:`universal_configuration` system: the configuration is a list of YAML
dictionaries, which are merged into one dictionary and written to the file
as YAML. The keys use the names from the `cloudflared documentation`__, so
any option supported by the :command:`cloudflared` configuration file can be
set this way, for example:

.. __: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/configure-tunnels/local-management/configuration-file/

- ``protocol`` -- connection protocol (``auto``, ``http2``, ``quic``)
- ``loglevel`` -- log verbosity (``debug``, ``info``, ``warn``, ``error``,
  ``fatal``)
- ``metrics`` -- address of the Prometheus metrics endpoint
- ``edge-ip-version`` -- IP version used to connect to the Cloudflare edge
  (``auto``, ``4``, ``6``)
- ``retries``, ``grace-period``, ``post-quantum``
- ``logfile`` -- path of the log file, for example in
  :envvar:`cloudflared__log_dir`
- ``originRequest`` -- default origin parameters for all ingress rules, for
  example ``connectTimeout``, ``noTLSVerify``, ``originServerName``,
  ``httpHostHeader`` or ``access``
- ``warp-routing`` -- parameters of the private network routing:
  ``connectTimeout``, ``maxActiveFlows``, ``tcpKeepAlive``
- ``ingress`` -- list of ingress rules, used in the ``local`` mode

The configuration of a tunnel is merged from the
:envvar:`cloudflared__default_configuration`,
:envvar:`cloudflared__configuration`,
:envvar:`cloudflared__group_configuration` and
:envvar:`cloudflared__host_configuration` lists, which apply to all tunnels
on a host, followed by the ``configuration`` parameter of the tunnel. The
``configuration`` parameters of the tunnel entries with the same name in
:ref:`cloudflared__ref_tunnels` are merged first, in the order of these
entries.

The role then adds the options which depend on the tunnel mode, replacing
the same options set in the configuration lists. In the ``local`` mode these
are ``tunnel``, ``credentials-file`` and ``ingress``. Each ingress rule
supports the ``hostname``, ``path``, ``service`` and ``originRequest`` keys;
the ``service`` key can point to an HTTP or HTTPS origin
(``http://127.0.0.1:80``), a TCP or SSH origin (``tcp://127.0.0.1:5432``,
``ssh://127.0.0.1:22``), a UNIX socket (``unix:/path/to/socket``), the
built-in ``hello_world`` server or a static ``http_status:NNN`` response.
:command:`cloudflared` requires the last rule to match all requests; if the
last rule has a ``hostname`` or ``path``, the role appends a rule with the
service from the ``catch_all_service`` parameter of the tunnel. The
generated file is checked with ``cloudflared tunnel ingress validate``
before it replaces the current one.

In the ``token`` mode the role adds the ``token-file`` option. The ingress
rules are managed in the Cloudflare dashboard and the ``ingress`` option is
ignored by :command:`cloudflared`.

Syntax
~~~~~~

Each entry of the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the configuration entry, not used in the configuration
  file. An entry with the same name as an earlier entry replaces it, together
  with its whole ``config`` dictionary, but keeps the position of the first
  entry with that name. Entries with different names are merged.

``config``
  Required. YAML dictionary with :command:`cloudflared` configuration
  options. The ``config`` dictionaries of all entries are merged recursively
  in the order of the entries, so an entry can add a key to the
  ``originRequest`` dictionary defined by an earlier entry. Lists are not
  merged, a later list replaces an earlier one; keep all ingress rules of
  a tunnel in one entry, for example named ``ingress``, and replace that
  entry to change them. An entry which replaces an earlier one is merged at
  the position of the earlier entry, so options set by entries between them
  still take precedence; set each option in one entry only, or change the
  order with the ``weight`` parameter described in
  :ref:`universal_configuration`.

``state``
  Optional. If ``present``, the entry is included in the configuration file.
  If ``absent``, the entry is not included, which removes an entry with the
  same name defined earlier. If ``ignore``, the entry is not evaluated by the
  role. If not specified, the entry keeps the state of an earlier entry with
  the same name, or ``present`` if there is none; an entry which should bring
  back an option removed earlier, for example in the group inventory, needs
  ``state: 'present'``. The ``configuration`` parameters of a tunnel are
  merged before they are added to the other lists, so their entries without
  ``state`` keep the state of an earlier entry of the same tunnel only, and
  are included even when the same name is removed for all tunnels.

Examples
~~~~~~~~

Use the HTTP/2 protocol and reduce the log verbosity of all tunnels in an
inventory group:

.. code-block:: yaml

   cloudflared__group_configuration:

     - name: 'protocol'
       config:
         protocol: 'http2'

     - name: 'loglevel'
       config:
         loglevel: 'warn'

Use the default log verbosity of :command:`cloudflared` on a specific host
in that group:

.. code-block:: yaml

   cloudflared__host_configuration:

     - name: 'loglevel'
       state: 'absent'

A tunnel defined for a group of hosts, with the origin parameters and the
ingress rules:

.. code-block:: yaml

   cloudflared__group_tunnels:
     - name: 'web'
       mode: 'local'
       tunnel_uuid: '6ff42ae2-765d-4adf-8112-31c55c1551ef'
       configuration:

         - name: 'originRequest'
           config:
             originRequest:
               connectTimeout: '30s'
               noTLSVerify: True

         - name: 'ingress'
           config:
             ingress:
               - hostname: 'app.example.com'
                 service: 'https://127.0.0.1:443'

A specific host changes one of the origin parameters and replaces the
ingress rules; the other origin parameter is kept:

.. code-block:: yaml

   cloudflared__host_tunnels:
     - name: 'web'
       configuration:

         - name: 'connectTimeout'
           config:
             originRequest:
               connectTimeout: '10s'

         - name: 'ingress'
           config:
             ingress:
               - hostname: 'app.example.com'
                 service: 'https://127.0.0.1:443'
               - hostname: 'admin.example.com'
                 service: 'https://127.0.0.1:8443'
