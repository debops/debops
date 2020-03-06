.. Copyright (C) 2013-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016 Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`ferm`_ is a wrapper around the :command:`iptables` and the :command:`ip6tables` commands which lets
you manage host firewalls in an easy and Ansible-friendly way. This role can
be used to setup firewall rules directly from the inventory, or it can be used
as a dependency by other roles to setup firewall rules for other services.

.. _ferm: http://ferm.foo-projects.org/
