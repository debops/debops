.. Copyright (C) 2015 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`stunnel`_ can be used to create encrypted TCP tunnels between two service
ports, either on the same host or on separate hosts.

Encryption is done using SSL certificates. This Ansible role can be used to
create tunnels between two or more hosts, using Ansible inventory groups.

.. _stunnel: https://stunnel.org/
