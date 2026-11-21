.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Garage`__ is a lightweight S3-compatible object store designed for
self-hosted and geo-distributed deployments. The ``debops.garage``
Ansible role installs the official static musl binary, writes
:file:`/etc/garage.toml`, and manages a single ``garage.service`` unit.
A one-host inventory produces a working S3 endpoint in a single play:
the daemon's ``--single-node`` flag creates the cluster layout, and an
optional ``--default-bucket`` flag creates a bucket and access key.
TLS always terminates on :ref:`debops.nginx` because Garage has no
native TLS. Binary upgrades are gated so that a minor rolling update
cannot silently become a major protocol change.

.. __: https://garagehq.deuxfleurs.fr/
