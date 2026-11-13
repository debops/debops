.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`debops ssh` command connects to a host of the Ansible
inventory over SSH. The inventory of the active view supplies the
connection parameters: the address, the user, the port, the private key and
the jump hosts. The options of the command override the inventory values,
the same way :command:`ssh` options override its configuration.

The destination follows the grammar of :command:`ssh`: ``[user@]hostname``
or the ``ssh://[user@]hostname[:port]`` form. The name before the ``@``
and the port of the URI override the inventory values. A remote command
written after the destination runs on the host, as in :command:`ssh`:

.. code-block:: console

   alice@controller:~$ debops ssh web-1 uname -r

The ``--`` marker before the destination hands the rest of the arguments to
:command:`ssh` verbatim. The inventory is not consulted and the known_hosts
store of the project is not applied; the command behaves like the plain
:command:`ssh` binary. The options which DebOps interprets still apply in
front of the marker. The marker after the destination separates the remote
command from the options.

With the ``-a|--accept`` option, the first connection to a host accepts an
unseen SSH host key and stores it in the active known_hosts store. Without
the option, :command:`ssh` refuses an unseen key and the connection fails.
A key which changes later is refused either way.

The ``rescan`` subcommand refreshes the known_hosts entries of the hosts
which match the Ansible inventory patterns: ``all``, the group names, the
wildcards and the unions. For each host, the stale entries of all of its
identifiers are removed from the store and the current host keys are
scanned and written. A host which fails a phase is reported; the remaining
hosts continue. The ``--remove`` and ``--scan`` options limit the run to
one phase.

The ``config`` subcommand prints the managed SSH client configuration block
of the project. With the ``--write`` option, the block is written into the
:file:`~/.ssh/config` file, so that a plain :command:`ssh` outside of
DebOps trusts the same hosts.
