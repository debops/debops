.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops scp`
---------------------

Copy a file to a host of the inventory:

.. code-block:: console

   alice@controller:~$ debops scp notes.txt web-1:/tmp/notes.txt

Copy a file back and accept an unseen host key on the first contact:

.. code-block:: console

   alice@controller:~$ debops scp -a web-1:/var/log/syslog ./syslog

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for the connections. If
  not specified, the default view will be used automatically. Using this
  option overrides the automatic view detection performed by DebOps based on
  the current working directory.

``-i <key>, --identity <key>``
  Use this private key for both connections, instead of the keys defined in
  the inventory. When the two operands resolve to different keys and no
  identity is specified, the command reports the difference and uses none of
  them.

``-a, --accept``
  Accept an unseen SSH host key on the first contact, for both connections.

``--eval``
  Do not copy; instead print the composed :command:`scp` command to stdout.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<source> ...``, ``<destination>``
  The file operands, in the ``[[user@]host:]path`` form. The last operand
  is the destination, the ones before it are the sources, as in
  :command:`scp`. A local path copies from or to the controller; a host
  name in an operand resolves through the inventory of the active view. The composed SSH options apply to both
  connections: when the operands resolve to different jump hosts, different
  ports or different private keys, the command reports the difference and
  applies none of the conflicting values.

The forwards and the stream options which the inventory defines for a host
do not apply to a file transfer. The command drops them and reports the
drop.

``<scp_options>``
  Any other options are passed to :command:`scp` unchanged, after the
  operands.
