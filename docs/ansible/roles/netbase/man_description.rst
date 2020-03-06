.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.netbase`` Ansible role manages the hostname stored in
:file:`/etc/hostname`, as well as the local host and network database located
in :file:`/etc/hosts` and :file:`/etc/networks` files, respectively.  It can be
used as a substitute for a DNS service for small number of hosts; with bigger
network or larger clusters usage of a real DNS server is preferred.
