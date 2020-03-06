.. Copyright (C) 2014-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The `dhcp_probe <https://www.net.princeton.edu/software/dhcp_probe/>`__ tool
can be used to passively detect rogue DHCP servers on IPv4 networks. Upon
detection, the service can execute custom commands to, for example, block the
culprit via RADIUS or notify the system administrator.

The ``debops.dhcp_probe`` role can be used to install and configure
:command:`dhcp_probe` on a Debian/Ubuntu host. It will utilize
:command:`systemd` instance templates to run DHCP Probe instances on multiple
network interfaces at once. By default, an e-mail message will be sent to the
system administrator with notification on newly detected rogue DHCP servers.
