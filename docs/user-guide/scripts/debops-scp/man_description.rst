.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops scp` command copies files to and from the hosts of
the Ansible inventory over SSH. The host names in the operands resolve
through the inventory of the active view. The view supplies the address,
the user, the port, the private key and the jump hosts.
