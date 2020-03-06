.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This Ansible role lets you manage one or multiple swap files. You can also
manage kernel parameters related to how swap is used by the system.

Note that this role can not setup a swap file on a BTRFS filesystem.

Refer to :ref:`debops.sysctl` for paging and swapping related kernel settings.
