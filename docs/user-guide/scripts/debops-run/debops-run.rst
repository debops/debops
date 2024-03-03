.. Copyright (C) 2021-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops run`
---------------------

Execute one or more Ansible Playbooks against the Ansible inventory. Playbooks
are included with the DebOps installation by default, they can be provided by
Ansible Collections or stored in the :file:`ansible/playbooks/` subdirectory in
the DebOps project directory. You can also specify full path to an Ansible
playbook on disk.

The :command:`debops run` command will automatically unlock and lock the
encrypted :file:`ansible/secret/` directory as needed, to give the playbooks
and roles access to secrets. If ``git-crypt`` is used for secret encryption,
this process might fail if the project directory contains uncommitted changes.
Easiest way to mitigate this is to unlock the project directory using the
``debops project unlock`` command before making any changes.

Options
~~~~~~~

The options below need to be specified before any playbooks to take effect.

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for running Ansible
  playbooks. If not specified, the default view will be used automatically.
  Using this option overrides the automatic view detection performed by DebOps
  based on the current working directory.

``-E, --bell``
  Emit an ASCII "bell" at the end of the :command:`ansible-playbook` command
  execution to notify the user. This might be useful during longer playbook
  runs.

``--eval``
  Do not execute :command:`ansible-playbook` command; instead print out all the
  environment variables and the command itself to stdout.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``--``
  Mark the end of the :command:`debops run` options. Any of the options after
  this mark will be passed to the :command:`ansible-playbook` command as-is.

``<[<namespace>.<collection>/]playbook>``
  Specify one or more Ansible Playbooks to execute.

  If you specify simple names like :file:`site`, :file:`service/core` and
  similar, the script will look for the corresponding playbooks in the default
  Ansible Collection (``debops.debops``). If not found there, the
  :file:`ansible/playbooks/` subdirectory in the current DebOps project
  directory will be checked next. Finally the name will be assumed to be
  a normal filesystem path with optional ``.yml`` or ``.yaml`` extension.

  You can also specify the namespace and collection at the start of the path to
  select a specific collection instead of the default one, for example
  :file:`debops.debops/site` or :file:`debops.debops/service/core`. The
  playbooks should be stored in the :file:`playbooks/` subdirectory of the
  Ansible Collection, you can use subdirectories to manage a large set of
  playbooks easier.

``[ansible_args]``
  You can specify all arguments supported by the :command:`ansible-playbook`
  command to augment the execution, for example ``--diff``, ``--check``,
  ``--limit``, and so on. See :command:`ansible-playbook --help` for more
  details.

Examples
~~~~~~~~

Execute the :file:`site.yml` DebOps playbook against all hosts in the Ansible
inventory:

.. code-block:: shell

   debops run site

Run the :file:`layer/common.yml` DebOps playbook against specific hosts in the
Ansible inventory. User will be notified at the end of playbook execution:

.. code-block:: shell

   debops run -E layer/common -l webserver,dbserver,appserver

Display the commands which will run a DebOps playbook for a specific service on
specific hosts:

.. code-block:: shell

   debops run --eval service/mariadb_server -l dbservers

Do the same as above, by specifying the Ansible Collection in which to look for
the playbook:

.. code-block:: shell

   debops run --eval debops.debops/service/mariadb_server -l dbservers

Run a playbook from a custom Ansible Collection in a specific "infrastructure
view" meant to be used to deploy an application:

.. code-block:: shell

   debops run -V deployment company.collection/app/setup -l appservers

Run a playbook with DebOps in a verbose debug mode:

.. code-block:: shell

   debops run -vvv service/sshd -l webserver

Same as above, but also enable verbose debug mode in Ansible itself:

.. code-block:: shell

   debops run -vvv service/sshd -l webserver -vvv

:command:`debops check`
-----------------------

Execute one or more Ansible Playbooks against the Ansible inventory in check
mode. This command behaves the same as the :command:`debops run` command, but
automatically adds the ``--diff`` and ``--check`` :command:`ansible-playbook`
options to enable the "check mode". In this mode, Ansible will execute the
playbook without making any actual changes to the host.
