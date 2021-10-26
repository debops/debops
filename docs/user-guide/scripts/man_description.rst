.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The DebOps project is a set of Ansible playbooks, roles, and optional scripts
which can be used to manage IT infrastructure based on Debian or Ubuntu
operating systems, from singhle hosts to entire data centers. The project can
be used to bootstrap bare metal environment, set up local DNS, DHCP, PXEboot
services and from there install and configure Debian or Ubuntu hardware and
virtual machines, as well as LXC and Docker containers.

DebOps includes a set of Python scripts which provide a wrapper around Ansible
and other tools. The scripts can be used to create and maintain "project
directories" which contain Ansible inventory, any installed Ansible Collections
and other data related to a given environment. You can also execute Ansible
playbooks from DebOps or other Ansible Collections as well as your own
playbooks using simple commands against the current environment.
