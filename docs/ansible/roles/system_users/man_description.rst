.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.system_users`` Ansible role can be used to manage local user
accounts and groups. The role allows for certain operations inside of the home
directories, like configuration of the mail forwarding, SSH public keys or
automatic deployment of user configuration files (dotfiles).

This role is designed to manage the local system administrator accounts, and
its behaviour will change if the support for LDAP is configured on a host. You
can also use the :ref:`debops.users` role which provides similar functionality,
but is designed to manage regular user accounts and application accounts,
without special modifications related to LDAP support.
