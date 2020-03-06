.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The `radvd <https://en.wikipedia.org/wiki/Radvd>`_, Router Advertisement
Daemon, is used to publish IPv6 subnets, routes, DNS configuration to other
hosts on the local network. It's required for the hosts to use SLAAC
autoconfiguration.

The ``debops.radvd`` Ansible role can be used to install and configure the
:command:`radvd` service. It will detect and automatically configure any
network bridges with IPv6 networking enabled.
