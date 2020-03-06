.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`tinc`__ is a Virtual Private Network daemon, it can be used to create encrypted
and tunneled connections to other hosts, forming a separate network, either
a centralized or a mesh one.

``debops.tinc`` Ansible role allows you to install and configure a mesh VPN
using ``tinc``, including automatic public key exchange between all hosts in
the Ansible inventory, connection to external hosts and secure configuration.

.. __: https://tinc-vpn.org/
