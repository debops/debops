.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This role manages the HTTP/HTTPS/FTP proxy configuration for APT. You can
define what proxy to use, what hosts should be connected to directly, as well
as set additional APT configuration options related to proxies as needed.

The role also features proxy online detection support to silently
skip/ignore temporally offline proxies which can make sense for
workstations and home servers.
