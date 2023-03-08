.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :man:`systemd-resolved(8)` service is a part of the `systemd`__ project.
The service is a local DNS resolver that can manage the
:file:`/etc/resolv.conf` configuration file and provide name resolution,
Multicast DNS and LLDP capabilities, among other things.

.. __: https://www.freedesktop.org/wiki/Software/systemd/

The :ref:`debops.resolved` Ansible role manages the :command:`systemd-resolved`
configuration. Other parts of the :command:`systemd` ecosystem are managed by
separate Ansible roles.
