.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _ssh_suite:

The DebOps SSH suite
====================

The DebOps SSH suite is a set of three commands, :command:`debops ssh`,
:command:`debops scp` and :command:`debops sftp`. They connect to the hosts
of the Ansible inventory over SSH. You do not write connection parameters:
the inventory supplies them. The suite is useful when you want to reach a
host of your environment without writing a playbook first.

.. contents::
   :depth: 2


Connecting to a host
--------------------

To open an SSH session on a host of the inventory, run:

.. code-block:: console

   alice@controller:~$ debops ssh web-1

DebOps looks up :literal:`web-1` in the inventory of the active view and
composes the :command:`ssh` command from the inventory facts: the
``ansible_host`` address, the ``ansible_user`` account,
the ``ansible_port`` port, the private key of the
``ansible_ssh_private_key_file`` variable and the jump hosts of
the ``ansible_ssh_common_args`` variable. Your own options
override the inventory values:

.. code-block:: console

   alice@controller:~$ debops ssh -u alice -p 2222 web-1

The destination accepts the forms which :command:`ssh` accepts:
``[user@]hostname`` and the ``ssh://[user@]hostname[:port]`` URI. The user
and the port written in the destination override the inventory values.

A remote command written after the destination runs on the host, the same
way as in :command:`ssh`:

.. code-block:: console

   alice@controller:~$ debops ssh web-1 uname -r

The ``--`` marker before the destination hands the rest of the arguments to
:command:`ssh` verbatim. The inventory is not consulted and the command
behaves like the plain :command:`ssh` binary. This is the way to use the
options of :command:`ssh` itself:

.. code-block:: console

   alice@controller:~$ debops ssh -- -G web-1


Copying files
-------------

To copy a file to a host of the inventory, run:

.. code-block:: console

   alice@controller:~$ debops scp notes.txt web-1:/tmp/notes.txt

To copy a file back:

.. code-block:: console

   alice@controller:~$ debops scp web-1:/var/log/syslog ./syslog

Both operands accept the ``[[user@]host:]path`` form of :command:`scp`, a
local path or a remote path. A remote path without a user uses the account
which the inventory defines.

.. warning::

   The composed SSH options apply to both connections of the command. When
   the two operands resolve to hosts with different jump hosts, different
   ports or different private keys, the command reports the difference and
   applies none of the conflicting values. Copy between such hosts with two
   :command:`debops scp` runs through a temporary file, or configure the
   connections in the :file:`~/.ssh/config` file.


File transfer sessions
----------------------

To open an interactive file transfer session, run:

.. code-block:: console

   alice@controller:~$ debops sftp web-1

The optional ``:path`` part of the destination selects the directory in
which the session starts:

.. code-block:: console

   alice@controller:~$ debops sftp web-1:/srv/files

For scripted transfers, write the commands into a batch file and pass it
with the ``-b`` option of :command:`sftp`:

.. code-block:: console

   alice@controller:~$ debops sftp -b batch web-1

A batch file holds one :command:`sftp` command per line:

.. code-block:: none

   put notes.txt /srv/files/notes.txt
   get /var/log/syslog syslog.log

The options which DebOps does not interpret are passed to :command:`sftp`
unchanged, in front of the destination or after it, in the place they were
written. The ``-a`` option of :command:`sftp` resumes an interrupted
transfer and passes through unchanged; the option of DebOps which accepts
an unseen host key is the long ``--accept`` form.


First contact
-------------

The first connection to a new host stops. :command:`ssh` asks about the
host key, and in a script it refuses the key and the connection fails. The
``--accept`` option accepts an unseen host key on the first contact
and stores it:

.. code-block:: console

   alice@controller:~$ debops ssh --accept web-1

A key which changes later is refused either way. The option accepts only
keys which are not known yet. When a host presents a different key than the
stored one, remove the stored key with :command:`debops ssh rescan` and
connect again.

The option exists on all of the commands which connect: :command:`debops
ssh`, :command:`debops scp`, :command:`debops sftp`, as well as
:command:`debops exec` and :command:`debops run`. On the commands which
compose an ssh command line the option is the long ``--accept`` form: the
short ``-a`` belongs to the underlying commands, which disable the
authentication agent forwarding (:command:`ssh`) or resume interrupted
transfers (:command:`sftp`) with it, and passes through unchanged.

Two other short options belong to DebOps itself: ``-v`` increases the
DebOps verbosity and ``-V`` selects the infrastructure view. The
``-v`` of :command:`ssh`, which turns its debugging on, and the
``-V`` of :command:`ssh`, which prints its version, reach the command
only after the ``--`` marker:

.. code-block:: console

   alice@controller:~$ debops ssh -- -v web-1


The known_hosts store of the project
------------------------------------

By default, DebOps leaves the SSH host keys to the operator's own
:file:`~/.ssh/known_hosts` file. The ``views.<view>.ssh.known_hosts``
configuration option moves the trust into the project:

``views.<view>.ssh.known_hosts``
  Type: string, ``user`` or ``project``.
  Purpose: selects where the SSH host keys of the inventory hosts are
  stored. The ``project`` mode gives each infrastructure view its own
  known_hosts store.
  Default: ``user``
  Example:

  .. code-block:: toml

     [views.system.ssh]
     known_hosts = "project"

In the ``project`` mode, each view of the project carries its own store:

.. code-block:: none

   project/
   └── .debops/
       └── ssh/
           └── views/
               └── system/
                   └── known_hosts

Three properties of the store matter:

- The store **replaces** the :file:`~/.ssh/known_hosts` file, it does not
  extend it. The keys of your own file are not consulted for the hosts of
  the project, and the keys of a host you already trust elsewhere are not
  carried over.
- The :file:`.debops/ssh/` directory is private, with the ``0700``
  permissions of a real :file:`~/.ssh` directory.
- The store is runtime state. The :file:`.gitignore` of the project ignores
  the :file:`known_hosts` files, and the rest of the
  :file:`.debops/ssh/` tree stays available for other uses.

The ``user`` mode and the ``project`` mode can be active at the same time
in different views. A view which does not declare a store stays on the
operator's own known_hosts file, even when the ``project`` mode is
selected.

The store is declared by the ``view-<view>-ssh.toml`` drop-in of the
project configuration, which DebOps writes when the project is created.
The drop-in carries the connection arguments of the view: the defaults of
the Ansible ``ssh_args`` option next to the store declaration, so that
the store does not replace them and the connections of Ansible keep
their multiplexing. The file belongs to the project once created;
``debops project refresh`` rewrites the generated ``ansible.cfg`` from
it but does not rewrite the drop-in itself.


Keeping the trust current
-------------------------

Containers are recreated, and a recreated container presents a new SSH host
key. The stale key in the store makes :command:`ssh` refuse the connection.
The ``rescan`` subcommand fixes this: it removes the stored entries of a
host and scans the current host keys:

.. code-block:: console

   alice@controller:~$ debops ssh rescan web-1

The arguments of ``rescan`` are the Ansible inventory patterns, so a whole
group or the whole inventory can be refreshed at once:

.. code-block:: console

   alice@controller:~$ debops ssh rescan all
   alice@controller:~$ debops ssh rescan webservers

For each host, the entries of all of its identifiers are removed: the
inventory name, the connection address and the addresses the names resolve
to. Then the current host keys of the host are scanned and written. A host
without a running SSH daemon is reported; the remaining hosts continue.

.. note::

   The scan trusts the key which the SSH daemon serves at the time of the
   scan. Run ``rescan`` after the provisioning of a host and before the
   first playbook run, so that the scanned keys match the host you meant to
   reach.

When the DNS zone of the hosts publishes SSHFP records, rescan verifies
the scanned keys against them. Keys which match records that a
DNSSEC-validating resolver authenticated are stored without
confirmation; keys which contradict the records are refused with a
report, because a mismatch means the host on the network is not the
host the DNS describes. Hosts without SSHFP records are handled as
before. The ``--no-dns`` option skips the DNS check entirely, and
``--dns-verify`` refuses hosts whose records the resolver did not
authenticate, even with ``--confirm``.

A match against records which the resolver did not authenticate
grants no trust: RFC 4255, which defines the SSHFP record, forbids
trusting unauthenticated SSHFP records. What happens to such keys is
a matter of policy:

``ssh.rescan.trust_unsigned_records``
  Type: boolean.
  Purpose: selects the handling of an SSHFP match which the resolver
  did not authenticate. With ``true``, the default, the match grants
  no trust and the keys are handled like the keys of hosts without
  SSHFP records: stored as scanned, or confirmed by the operator with
  the ``--confirm`` option. With ``false``, such hosts are not stored;
  run the rescan with ``--confirm`` to accept the keys after checking
  the fingerprints.

.. note::

   SSHFP verification is as strong as the DNS answer. On a
   DNSSEC-signed zone the records are authenticated and the match is a
   genuine third-party verification; on an unsigned zone the match is
   trust in DNS, and the option above decides whether it may confirm
   anything.

With the ``-c|--confirm`` option, rescan shows the fingerprints of the
scanned keys in the form which ``ssh-keygen -l`` prints and asks for
each host before storing them - press Enter to accept, Ctrl-C to abort
the whole run.

Run ``rescan`` when a host was provisioned or recreated, before the first
connection to it.


Using plain ssh outside of DebOps
---------------------------------

The connection parameters of the inventory work inside of DebOps commands.
To make a plain :command:`ssh` outside of DebOps reach the same hosts, the
``config`` subcommand prints an SSH client configuration block for the
hosts of the project:

.. code-block:: console

   alice@controller:~$ debops ssh config

With the ``--write`` option, the block is written into your
:file:`~/.ssh/config` file. The block adds the known_hosts store of the
project as an additional host key source next to your own, so both sources
are trusted and the new keys of foreign hosts still land in your own file.


See also
--------

- :ref:`cmd_debops-ssh`, :ref:`cmd_debops-scp` and :ref:`cmd_debops-sftp`
  manual pages for the complete option reference
- :ref:`project_directory` for the layout of the project directory
- :ref:`debops_configuration` for the configuration system
