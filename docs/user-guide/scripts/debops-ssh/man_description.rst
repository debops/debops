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
:command:`ssh` verbatim. The inventory is not consulted. The options of
DebOps still apply in front of the marker, ``--accept`` among them -- with
it, the known_hosts store of the project is applied to the handoff as
well. The options which DebOps interprets still apply in
front of the marker. The marker after the destination separates the remote
command from the options.

With the ``--accept`` option, the first connection to a host accepts an
unseen SSH host key and stores it in the active known_hosts store. Without
the option, :command:`ssh` refuses an unseen key and the connection fails.
A key which changes later is refused either way. The short ``-a`` belongs
to :command:`ssh`, which disables the authentication agent forwarding with
it, and passes through unchanged.

The ``rescan`` subcommand refreshes the known_hosts entries of the hosts
which match the Ansible inventory patterns: ``all``, the group names, the
wildcards and the unions. For each host, the current host keys are
scanned first and held in memory. With the ``--dns`` mode (the
default), keys whose fingerprints match SSHFP records which a
DNSSEC-validating resolver authenticated are accepted automatically,
keys which contradict the published records are refused with a report,
and hosts without usable records fall back to the confirmation prompt
or the plain store operation. A match which the resolver did not
authenticate grants no trust of its own; the
``ssh.rescan.trust_unsigned_records`` option of the configuration
selects what happens to such keys. The ``--dns-verify`` option
requires a DNSSEC-validating resolver to authenticate the DNS answer
before a match is trusted. The ``--no-dns`` option skips the DNS check
entirely. After the keys are accepted, the stored entries of the
identifiers which answered the scan are removed from the store and the
accepted keys are appended; the entries of the other identifiers, and
of a host whose keys were refused, stay as they are. A host which
fails a phase is reported; the remaining hosts continue. The
``--remove`` and ``--scan`` options limit the run to one phase. The
``-c|--confirm`` option shows the scanned fingerprints in the form
which :command:`ssh-keygen -l` prints and asks for each host before
storing them.

The ``config`` subcommand prints the managed SSH client configuration block
of the project. With the ``--write`` option, the block is written into the
:file:`~/.ssh/config` file, so that a plain :command:`ssh` outside of
DebOps trusts the same hosts.
