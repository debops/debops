.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops ssh`
---------------------

Connect to a host of the Ansible inventory:

.. code-block:: console

   alice@controller:~$ debops ssh web-1

Run a remote command, accept an unseen host key on the first contact:

.. code-block:: console

   alice@controller:~$ debops ssh -a web-1 'uname -r'

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for the connection. If
  not specified, the default view will be used automatically. Using this
  option overrides the automatic view detection performed by DebOps based on
  the current working directory.

``-u <name>, --user <name>``
  Connect as this user instead of the account defined in the inventory.

``-p <port>, --port <port>``
  Connect to this port instead of the port defined in the inventory.

``-i <key>, --identity <key>``
  Use this private key instead of the key defined in the inventory.

``-a, --accept``
  Accept an unseen SSH host key on the first contact and store it in the
  active known_hosts store. Without the option, :command:`ssh` refuses an
  unseen key and the connection fails. A key which changes later is refused
  either way.

``--eval``
  Do not connect; instead print the composed :command:`ssh` command to
  stdout.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<destination>``
  The host to connect to, in the ``[user@]hostname`` form or the
  ``ssh://[user@]hostname[:port]`` form. The host name resolves through the
  inventory of the active view. A destination which is an inventory pattern
  is rejected; the patterns belong to the ``rescan`` subcommand.

``<remote_command> ...``
  A remote command written after the destination runs on the host, as in
  :command:`ssh`. Everything after the destination is passed to the remote
  shell.

``--``
  Before the destination, the marker hands the rest of the arguments to
  :command:`ssh` verbatim: the inventory is not consulted and the
  known_hosts store of the project is not applied. After the destination,
  the marker separates the remote command from the options.

The ``rescan`` subcommand
-------------------------

The ``rescan`` subcommand refreshes the known_hosts entries of the hosts
which match the Ansible inventory patterns. It removes the stale entries of
every identifier of a host and scans the current host keys:

.. code-block:: console

   alice@controller:~$ debops ssh rescan webservers

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for the rescan.

``--remove``
  Only remove the stored entries of the hosts; do not scan the current
  keys.

``--scan``
  Only scan and store the current host keys; do not remove the stored
  entries.

``--eval``
  Do not refresh anything; instead print the actions which would be
  performed, as the commands which perform them.

``-f <file>, --known-hosts-file <file>``
  Operate on this known_hosts file instead of the store of the active mode.

``-T <seconds>, --timeout <seconds>``
  Timeout of each key scan (default: ``10``).

``--dns``
  Verify the scanned host keys against the SSHFP records of the DNS
  (the default). Keys which match the published records are stored
  without confirmation; keys which contradict the records are refused
  with a report.

``--no-dns``
  Do not check the SSH host keys against DNS.

``--dns-verify``
  Store keys automatically only when a DNSSEC-validating resolver
  authenticated the SSHFP records of the DNS.

``-c, --confirm``
  Show the scanned fingerprints in the form which
  :command:`ssh-keygen -l` prints and ask for each host before storing
  them.

``<pattern> ...``
  One or more Ansible inventory patterns: ``all``, the group names, the
  wildcards and the unions. A pattern which matches no host is reported;
  the remaining hosts continue.

The ``config`` subcommand
-------------------------

The ``config`` subcommand prints the managed SSH client configuration block
of the project. With the ``--write`` option, the block is written into the
:file:`~/.ssh/config` file, so that a plain :command:`ssh` outside of
DebOps trusts the same hosts.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for the block.

``--write``
  Write the managed block into the :file:`~/.ssh/config` file of the
  operator. Without the option, the block is printed to stdout.
