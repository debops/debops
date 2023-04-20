.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops env`
---------------------

Without additional arguments, it will display the variables which will be
present at runtime in the process environment. Any arguments that are unknown
to the subcommand will be treated as an external command to execute within the
DebOps project environment. This might be useful to run various Ansible
commands with a proper ``$ANSIBLE_CONFIG`` environment variable and other
variables defined by the user.

If a project directory contains encrypted secrets, they will be automatically
unlocked before executing the external command and locked afterwards if
necessary.


Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to use for executing commands.
  If not specified, the default view will be used automatically. Using this
  option overrides the automatic view detection performed by DebOps based on
  the current working directory.

``--scope full|local``
  Specify if only the variables defined by DebOps should be displayed
  (``local``, default), or all variables present in the runtime environment
  (``full``).

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``command args``
  Specify a command to execute inside of the DebOps project environment, with
  all variables set at runtime. Any arguments specified after the command will
  be passed along as that command's arguments.


Examples
~~~~~~~~

Show environment variables defined by DebOps:

.. code-block:: shell

   debops env

Show all environment variables defined at DebOps runtime:

.. code-block:: shell

   debops env --scope full

Parse Ansible inventory and output its structure in a JSON format:

.. code-block:: shell

   debops env ansible-inventory --list | jq .

Parse Ansible inventory using non-default "infrastructure view":

.. code-block:: shell

   debops env -V deployment ansible-inventory --list

List Ansible collections accessible in the DebOps project directory:

.. code-block:: shell

   debops env ansible-galaxy collection list

Run a shell command within the scope of the DebOps project:

.. code-block:: shell

   debops env ansible-navigator


Environment files
-----------------

DebOps scripts support multiple configuration files which can be used to affect
its execution environment:

- :file:`/etc/default/debops` (per-system environment)

- :file:`$XDG_CONFIG_HOME/debops/environment` (per-user environment)

- :file:`<project directory>/.debops/environment` (per-project environment)

- :file:`<project directory>/.env` (per-project environment ignored by version
  control)

To see the list of the environment files used for configuration, you can run
the command:

.. code-block:: shell

   debops config list

You can use these files to store environment variables which are then added to
the runtime environment of the :command:`debops` subcommands and processes
executed through them. One of the more important variables is
``$ANSIBLE_CONFIG`` which specifies the path to the :file:`ansible.cfg`
configuration file. This variable is generated dynamically by DebOps based on
the current project and view directories, and cannot be overridden from the
configuration files.

Environment files are compatible with the `python-dotenv`__ project. Each
environment variable is specified as:

.. code-block:: shell

   NAME=value

Empty lines and lines starting with the ``#`` character are ignored.

.. __: https://pypi.org/project/python-dotenv/
