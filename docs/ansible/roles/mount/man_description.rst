.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.mount`` Ansible role can be used to manage local filesystem mounts
as well as bind mounts in the :file:`/etc/fstab` database. Custom directories
can also be created by this role, with support for normal as well as ACL
attributes.

This role is meant to be used to configure local filesystems, for remote
filesystems, you can use the :ref:`debops.nfs` role instead, which will
configure the NFS client service.
