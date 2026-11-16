.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops sftp` command runs an interactive file transfer
session with a host of the Ansible inventory. The host name of the
destination resolves through the inventory of the active view. The view
supplies the address, the user, the port, the private key and the jump
hosts. The optional path is the directory in which the session starts.
