.. Copyright (C) 2015-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`DebOps <http://www.debops.org/>`_ is a set of Python scripts, Ansible
playbooks and Ansible roles designed to work together to create a consistent
data center environment based on Debian GNU/Linux distribution.

This role installs the DebOps scripts, playbooks and roles on a specified host.
It can be used to create remote Ansible Controller hosts, which then can be
used to control other hosts using DebOps. Roles and playbooks will be installed
by default in a central, system-wide location, available to all users.
