.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`vmagent`__ is a small, fast metrics collector from the VictoriaMetrics
project. It scrapes Prometheus-compatible targets (and accepts data over
several push protocols), applies optional relabeling, and forwards the
resulting samples to one or more ``-remoteWrite.url`` endpoints with an
on-disk persistent queue for reliable delivery. The
``debops.vmagent`` Ansible role installs the ``vmagent`` binary from the
upstream VictoriaMetrics GitHub Releases (with full air-gap support for
internal mirrors, controller-side archives, or Packer-baked images) and
manages one or more named instances through a single ``vmagent@.service``
systemd template unit. Per-instance secrets (bearer tokens for
remote-write authentication) are sourced from the standard
:ref:`debops.secret` mechanism.

.. __: https://docs.victoriametrics.com/vmagent/
