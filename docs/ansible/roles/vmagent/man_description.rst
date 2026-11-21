.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`vmagent`__ is a small metrics agent from the VictoriaMetrics project. It
scrapes Prometheus-compatible targets (and accepts data over several push
protocols), applies optional relabeling, and forwards the samples to one or
more remote write endpoints, with an on-disk persistent queue for reliable
delivery. The ``debops.vmagent`` Ansible role installs the :command:`vmagent`
binary from the upstream release archive, verified with a SHA256 checksum and
downloaded from GitHub, an internal mirror or copied from the Ansible
Controller, and manages one or more instances through the ``vmagent@.service``
systemd template unit. Bearer tokens used for remote write are stored by the
:ref:`debops.secret` role.

.. __: https://docs.victoriametrics.com/victoriametrics/vmagent/
