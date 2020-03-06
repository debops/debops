.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.apt_install`` Ansible role is meant to be used as an easy way to
install APT packages on hosts that don't require more extensive configuration
which would require a more extensive, custom Ansible role. The role itself
exposes several Ansible default variables which can be used to specify custom
lists of packages on different levels of Ansible inventory (global, per-group
or per-host).
