.. Copyright (C) 2014-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2016 DebOps <http://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.tcpwrappers`` Ansible role can be used to manage entries in
``/etc/hosts.allow`` and ``/etc/hosts.deny`` which are used by TCP Wrappers to
limit connections to daemons that utilize the ``libwrap`` library.
