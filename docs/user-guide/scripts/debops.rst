.. Copyright (C) 2021-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _cmd_debops:

The :command:`debops` command
=============================

The :command:`debops` command provides multiple sub-commands, some of which are
split into sections.

:command:`debops project`
  This section includes commands used to create and maintain the "project
  directories" which contain one or multiple Ansible inventories, PKI
  infrastructure, GPG keyring, and other resources used in a particular
  environment.

:command:`debops exec`
  This command can be used to execute Ansible modules ad-hoc against a given
  environment. You can use any arguments accepted by the :command:`ansible`
  command - they will be executed in the DebOps project context, including the
  runtime environment variables and with the :file:`ansible/secret/` directory
  unlocked if necessary.

:command:`debops run`
  This command can be used to execute Ansible playbooks against a given
  environment. The playbooks used can come either from the DebOps Python
  package (included by default), from an Ansible Collection, or from the
  :file:`ansible/playbooks/` directory in a given project. You can also specify
  all :command:`ansible-playbook` arguments to affect the Ansible execution;

:command:`debops check`
  This command is the same as the ``debops run`` command above, but
  automatically adds the ``--diff`` and ``--check`` :command:`ansible-playbook`
  options to ensure that the playbooks are executed in a check mode;

:command:`debops env`
  This command can be used to inspect the environment variables which will be
  present when various DebOps commands are executed. It can also be used to run
  shell commands in DebOps environment, which is a handy shortcut for using
  Ansible ecosystem with DebOps project directories.

:command:`debops config`
  This command allows the user to inspect and manipulate the DebOps
  configuration options in various formats;

You can find more information about these subcommands in the DebOps
documentation, ``debops-*`` manual pages or by running them with the ``--help``
option.

Options
-------

``-h, --help``
  Display the help and usage information

``--version``
  Display the version of the :command:`debops` scripts


Verbose mode and logging
------------------------

The :command:`debops` script can send log messages about its operation to the
:command:`syslog` service. Using configuration options, users can specify where
to send the log messages, default log level and facility.

Users can specify the ``--verbose`` or ``-v`` flag in the :command:`debops`
subcommands to increase the script verbosity. The flag enables log output to the
standard error (stderr) stream. Multiple uses of the flag increase the log level
from the default ``WARNING`` to ``NOTICE``, ``INFO`` and ``DEBUG`` with ``-vvv``
respectively.

To view the logs from :command:`debops` using :command:`journald` service, run the command:

.. code-block:: console

   journalctl -f _COMM=debops


Environment variables
---------------------

These environment variables can be used to affect the environment during script
execution:

``DEBOPS_CMD_ANSIBLE``
  Path to the :command:`ansible` binary used by DebOps. Can be overridden by
  configuration files.

``DEBOPS_CMD_ANSIBLE_PLAYBOOK``
  Path to the :command:`ansible-playbook` binary used by DebOps. Can be
  overridden by configuration files.

``DEBOPS_CMD_GPG``
  Path to the :command:`gpg` binary used by DebOps. Can be overridden by
  configuration files.

``DEBOPS_CMD_ENCFS``
  Path to the :command:`encfs` binary used by DebOps. Can be overridden by
  configuration files.

``DEBOPS_CMD_UMOUNT``
  Path to the :command:`umount` binary used by DebOps on Darwin-based hosts.
  Can be overridden by configuration files.

``DEBOPS_CMD_FUSERMOUNT``
  Path to the :command:`fusermount` binary used by DebOps. Can be overridden by
  configuration files.
