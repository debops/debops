.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

``ifupdown`` is a set of high-level scripts in Debian/Ubuntu Linux
distributions which can be used to configure network interfaces, bridges, VLAN
interfaces, bonding, and so on. You can find example configuration and usage
guides on the `NetworkConfiguration`__ page of the `Debian Wiki`__.

``debops.ifupdown`` is an Ansible role which wraps ``ifupdown`` in an easy to
use, and Ansible-friendly interface. It aims to be a safe and reliable way to
let you configure network interfaces on hosts managed using Ansible. It can be
used either as a standalone role configured using role/inventory variables, or
as a dependency of another role, to provide network configuration as needed.

.. __: https://wiki.debian.org/NetworkConfiguration
.. __: https://wiki.debian.org/
