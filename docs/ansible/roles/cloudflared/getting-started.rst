.. Copyright (C) 2025 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2025 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


What is cloudflared?
--------------------

`cloudflared <https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/>`_
is the official Cloudflare Tunnel client. It maintains outbound-only encrypted
connections from your server to the Cloudflare network, eliminating the need to
open inbound firewall ports or have a public IP address on the origin server.

The ``debops.cloudflared`` role installs and configures cloudflared on
Debian/Ubuntu servers, managing one or more tunnel instances via systemd
template units (``cloudflared@<name>.service``).


Prerequisites
-------------

Before using this role, you need:

1. A Cloudflare account with at least one domain.

2. A Cloudflare Tunnel created either:

   - **Remotely** via the `Cloudflare Zero Trust dashboard
     <https://one.dash.cloudflare.com/>`_ (provides a tunnel token).

   - **Locally** via the ``cloudflared`` CLI on any machine::

        cloudflared tunnel login
        cloudflared tunnel create <tunnel-name>

     This produces a credentials JSON file.

3. The tunnel token or credentials file placed on the Ansible Controller
   in the appropriate ``secret/`` directory (see below).

Token-mode tunnels require :command:`cloudflared` 2025.4.0 or newer, which
can read the tunnel token from a file. The upstream APT repository provides
the current release. The role does not upgrade an already installed package;
if it is older, the role stops before the tunnel is configured.

The upstream Cloudflare APT key is identified by
:envvar:`cloudflared__apt_key_id` and downloaded from
:envvar:`cloudflared__apt_key_url` via :ref:`debops.keyring`. To pin a
reviewed copy of the key on the Ansible Controller, place an ASCII-armored
file named :file:`0x<FINGERPRINT>.asc` in :envvar:`keyring__local_path`
(see :ref:`debops.keyring`). That local file is used instead of the
vendor URL.


Tunnel modes
------------

The role supports two tunnel management modes:

**Token mode** (``mode: 'token'``, default)
  The tunnel is managed remotely via the Cloudflare dashboard. Ingress rules,
  DNS records, and other routing configuration are set in the Cloudflare UI
  or API. The role only needs the tunnel token to start the connector.

  Place the token in::

    secret/cloudflared/tunnels/<tunnel-name>/token

**Local mode** (``mode: 'local'``)
  The tunnel configuration (ingress rules, origin request settings, WARP
  routing) is managed locally via Ansible. The role generates a per-tunnel
  YAML file named :file:`<tunnel-name>.yml` under
  :envvar:`cloudflared__config_dir`.

  Place the credentials JSON (from ``cloudflared tunnel create``) in::

    secret/cloudflared/tunnels/<tunnel-name>/credentials.json


Secret management
-----------------

This role uses the standard DebOps ``secret`` mechanism to manage sensitive
tunnel credentials. Secrets are stored on the Ansible Controller under the
``secret/`` directory tree (typically ``../secret/`` relative to the inventory).

The role does not generate the tunnel secrets. Create a directory for each
tunnel and place the appropriate file in it before running the playbook:

- ``secret/cloudflared/tunnels/<name>/token`` -- for token-mode tunnels
- ``secret/cloudflared/tunnels/<name>/credentials.json`` -- for local-mode tunnels

The role checks that the file exists and stops with the expected path in
the error message otherwise. The file is copied to
:envvar:`cloudflared__credentials_dir` on the remote host, readable only by
the :command:`cloudflared` daemon, and referenced in the tunnel
configuration file, so that the secret is not exposed in the process
environment or on the command line.


Example inventory
-----------------

To manage cloudflared on a host, add it to the
``[debops_service_cloudflared]`` Ansible inventory group:

.. code-block:: ini

   [debops_service_cloudflared]
   hostname

Minimal token-mode configuration in ``host_vars/hostname/cloudflared.yml``:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'my-tunnel'

This expects the token file at
``secret/cloudflared/tunnels/my-tunnel/token``.

Local-mode configuration with ingress rules:

.. code-block:: yaml

   cloudflared__tunnels:
     - name: 'web-tunnel'
       mode: 'local'
       tunnel_uuid: '6ff42ae2-765d-4adf-8112-31c55c1551ef'
       config:
         ingress:
           - hostname: 'app.example.com'
             service: 'http://127.0.0.1:80'
           - hostname: 'api.example.com'
             service: 'http://127.0.0.1:8080'

The ``config`` dictionary is written to the tunnel configuration file as is,
see :ref:`cloudflared__ref_tunnels` for details.


Prometheus metrics
------------------

Each tunnel exposes Prometheus metrics on ``localhost``. Unless the
``metrics`` option is set in the tunnel configuration, :command:`cloudflared`
binds to the first free port from the ``20241`` - ``20245`` range, so on a
host with a single tunnel the metrics are available at
``http://127.0.0.1:20241/metrics``. The port ``20241`` is registered in
:file:`/etc/services` via the :ref:`debops.etc_services` role. On hosts with
several tunnels, set a fixed ``metrics`` address for each of them.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cloudflared`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/cloudflared.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution.

Available role tags:

``role::cloudflared``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::cloudflared``
  Skip the main role tasks, but run the role dependencies, for example the
  :ref:`debops.keyring` role which configures the APT repository.

``meta::facts``
  Update the Ansible local facts of the role.
