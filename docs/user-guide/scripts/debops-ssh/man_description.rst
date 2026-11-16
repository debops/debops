.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops ssh` command connects to a host of the Ansible
inventory over SSH. The connection parameters come from the inventory of
the active view. The options of the command override them. The
``rescan`` subcommand refreshes the known_hosts entries of the
inventory hosts. The ``config`` subcommand prints the managed SSH
client configuration block of the project.
