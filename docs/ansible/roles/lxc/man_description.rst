.. Copyright (C) 2014-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Linux Containers`__ or LXC provide a way to partition existing Linux hosts
into separate environments using Linux cgroups, namespace isolation, POSIX
capabilities and chrooted filesystems.

.. __: https://en.wikipedia.org/wiki/LXC

The ``debops.lxc`` Ansible role can be used to configure LXC support on
a Debian/Ubuntu host. It can manage configuration files in :file:`/etc/lxc/`
directory and provide custom scripts that allow, for example, initial
bootstrapping of the user's SSH public keys inside of the container so that it
can be managed remotely with Ansible.
