.. Copyright (C) 2015-2018 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2018-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.kmod`` Ansible role can be used to manage configuration of the
Linux kernel modules, located in the :file:`/etc/modprobe.d/` directory, and
specify what kernel modules should be loaded at boot time using configuration
in :file:`/etc/modules-load.d/` directory.

Kernel module configuration can be specified using Ansible inventory, or other
Ansible roles can use the ``debops.kmod`` role to configure kernel module
options on their behalf.
