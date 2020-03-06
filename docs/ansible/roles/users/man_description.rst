.. Copyright (C) 2013-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2019 <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.users`` Ansible role can be used to manage local user accounts and
groups. The role allows for certain operations inside of the home directories,
like configuration of the mail forwarding, SSH public keys or automatic
deployment of user configuration files (dotfiles).

This role is designed to manage regular user accounts and application accounts.
In a LDAP-enabled environment, it might be better to configure these using LDAP
directory, and manage local system administrator accounts using the
:ref:`debops.system_users` Ansible role.
