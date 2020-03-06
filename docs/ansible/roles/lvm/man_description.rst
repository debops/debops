.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Logical Volume Manager`_ lets you manage your disk space in a more elastic
way, separating physical hard disks from the logical volumes.

This Ansible role lets you configure :file:`/etc/lvm/lvm.conf` configuration file,
as well as gives you a set of variables which can be used to manage LVM logical
volumes, automatically create filesystems on them and mount them as needed.

.. _Logical Volume Manager: https://en.wikipedia.org/wiki/Logical_Volume_Manager_(Linux)
