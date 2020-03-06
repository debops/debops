.. Copyright (C) 2014-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.etc_services`` role can be used to "reserve" or "register" a
service port in the :file:`/etc/services` file. Service ports configured this way can
appear as named entries in many command outputs, such as :command:`iptables --list`
or :command:`netstat --listening --program`. You can also have convenient database
of reserved and free ports on a particular host, and reference ports by
their names in firewall configuration files.
