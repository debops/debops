.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops scp` command copies files to and from the hosts of the
Ansible inventory over SSH. The operands follow the grammar of
:command:`scp`: a local path, or a ``[[user@]host:]path`` form. A host name
in an operand resolves through the inventory of the active view, which
supplies the address, the user, the port, the private key and the jump
hosts.

The composed SSH options apply to both connections. Operands whose
inventory entries define different SSH ports or different private keys
are reported, and neither value is applied. The jump hosts are not
resolved per connection: one jump chain serves both connections; use the
:file:`~/.ssh/config` file for hosts which need their own.

The SSH options which configure port or packet forwards do not apply to a
file transfer. The command drops them and reports the drop.

With the ``--accept`` option, the first contact with a host accepts an
unseen SSH host key and stores it in the active known_hosts store.

The options which DebOps does not interpret are passed to :command:`scp`
unchanged, in front of the operands.
