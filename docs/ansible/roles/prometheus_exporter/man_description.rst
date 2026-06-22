.. Copyright (C) 2026 Patryk Sciborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This role installs and configures Prometheus exporters packaged in the
Debian / Ubuntu repositories (the ``prometheus-*-exporter`` family, e.g.
``prometheus-node-exporter``, ``prometheus-postgres-exporter``). Each
exporter is configured through a dedicated systemd drop-in file that resets
and rewrites ``ExecStart=`` (and, when needed, ``Environment=``), which makes
the role independent of per-package and per-release differences in the
shipped ``/etc/default/`` files. Exporters bind to the loopback interface by
default and are intended to be scraped by a local agent such as
:ref:`debops.vmagent`, which forwards the samples to a remote store.
