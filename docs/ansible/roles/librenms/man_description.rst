.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`LibreNMS`_ is a network monitoring dashboard written in PHP. It can use SNMP,
:program:`collectd`, :program:`check_mk` or other agents to gather data from variety of
devices (switches, routers, servers, etc.) and graph them using RRD. It's easy
to use, and can perform autodiscovery to find and monitor additional devices.

``debops.librenms`` role will manage a central LibreNMS monitoring host and web
interface.

.. _LibreNMS: http://www.librenms.org/
