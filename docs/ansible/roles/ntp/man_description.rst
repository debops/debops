.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

An NTP daemon is used for time synchronization, either on a local system as
a client, or on remote systems as a server.

The ``debops.ntp`` Ansible role supports multiple NTP servers, and is
container-aware so that an NTP server won't be installed inside containers.

The role is also used to configure the system timezone using the ``tzdata``
package.
