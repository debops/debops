.. Copyright (C) 2014-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`dnsmasq`__ is an application that provides DNS, DHCP, TFTP and Router
Advertisement services in a compact package, suitable for small, internal
networks. it's commonly used as a DNS cache and forwarder on desktop
workstations or servers.

.. __: http://www.thekelleys.org.uk/dnsmasq/doc.html

The ``debops.dnsmasq`` Ansible role can be used to configure :command:`dnsmasq`
on a given host. By default the DNS cache will be configured, but the role
checks for presence of different services like ``lxc-net`` configured by the
:ref:`debops.lxc`, :command:`consul` and specific network interfaces defined by
the :ref:`debops.ifupdown`, and adjusts the configuration automatically.
