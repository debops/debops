.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops exec`
----------------------

Execute an Ansible module against the Ansible inventory. The
`ansible.builtin.command`__ module is used by default, a different module can
be specified with the ``-m`` or ``--module-name`` parameter.

.. __: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/command_module.html

The :command:`debops exec` command will automatically unlock and lock the
encrypted :file:`ansible/secret/` directory as needed, to give the Ansible
module access to secrets.

Options
~~~~~~~

The options below need to be specified before any Ansible arguments to take
effect.

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for running Ansible
  commands. If not specified, the default view will be used automatically.
  Using this option overrides the automatic view detection performed by DebOps
  based on the current working directory.

``-E, --bell``
  Emit an ASCII "bell" at the end of the :command:`ansible` command execution
  to notify the user. This might be useful during longer module runs.

``--eval``
  Do not execute :command:`ansible` command; instead print out all the
  environment variables and the command itself to stdout.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--``
  Mark the end of the :command:`debops exec` options. Any of the options after
  this mark will be passed to the :command:`ansible` command as-is.

``[ansible_args]``
  You can specify all arguments supported by the :command:`ansible` command to
  augment the execution, for example ``--diff``, ``--check``, ``--become``, and
  so on. See :command:`ansible --help` for more details.

Examples
~~~~~~~~

Send a ping to all hosts in the Ansible inventory:

.. code-block:: shell

   debops exec all -m ping

Check what UNIX account is used to run Ansible commands using a specific
"infrastructure view":

.. code-block:: shell

   debops exec -V deployment hostname -a 'whoami'

Perform a full upgrade of a Debian host using APT:

.. code-block:: shell

   debops exec hostname -m apt -a 'upgrade=full' -b

Reboot all webservers with :man:`molly-guard(8)` protection, user will be
notified at the end of Ansible execution:

.. code-block:: shell

   debops exec -E webservers -b -m reboot -a 'search_paths=/lib/molly-guard'
