.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The UNIX system groups are used on Linux hosts for low level access control
mechanism for different system services. Debian by default creates a
`a set of UNIX system groups`__ which control access to various parts of the
system.

The ``debops.system_groups`` Ansible role is used to configure additional UNIX
system groups that are used on hosts managed by DebOps. It can also be used to
define :command:`sudo` and :command:`systemd-tmpfiles` configuration for these
UNIX groups.

Additionally, a simple Access Control List managed by the role in the Ansible
local facts can be used by other Ansible roles to configure access for selected
UNIX groups to the services managed by these roles.

.. __: https://wiki.debian.org/SystemGroups
