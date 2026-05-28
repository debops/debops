.. Copyright (C) 2025-2026 Marcin Sciborski <marcin@sciborski.com>
.. Copyright (C) 2025-2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2025-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Cloudflare Tunnel`__ (formerly Argo Tunnel) is a service from Cloudflare
that establishes outbound-only encrypted connections from an origin host to
the Cloudflare edge network, eliminating the need for inbound firewall
ports or a public IP address. The ``debops.cloudflared`` Ansible role
installs the ``cloudflared`` daemon from the upstream Cloudflare APT
repository (via :ref:`debops.keyring`) and manages one or more named
tunnel instances through a single ``cloudflared@.service`` systemd template
unit. Both Cloudflare-managed (token mode) and Ansible-managed (local
mode with inline ingress) tunnel configurations are supported, with
credentials sourced from the standard :ref:`debops.secret` mechanism.

.. __: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/
