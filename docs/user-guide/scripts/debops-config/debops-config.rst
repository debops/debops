.. Copyright (C) 2021-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops config env`
----------------------------

Display the variables which will be present at runtime in the process
environment.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``--scope full|local``
  Specify if only the variables defined by DebOps should be displayed
  (``local``, default), or all variables present in the runtime environment
  (``full``), similar to the output of the :man:`env(1)` command.

Examples
~~~~~~~~

Print environment variables defined by DebOps:

.. code-block:: shell

   debops config env


:command:`debops config get`
----------------------------

Output DebOps project configuration, optionally scoped to a specific context.
Multiple output formats are available (plain text, JSON, TOML, YAML).

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``--format json|toml|unix|yaml``
  Specify the format of the output. The default format is TOML which is
  considered human-friendly. The JSON format can be used to enable easy parsing
  by programs.

``key``
  Name of the configuration option key to return. Subkeys are specified using
  dot (``.``) as a separator. If not specified, entire configuration tree will
  be returned by default. Multiple keys may be specified, they will be returned
  in order of appearance.

Examples
~~~~~~~~

Print all configuration options to standard output:

.. code-block:: shell

   debops config get

Display the "system view" configuration options in TOML format:

.. code-block:: shell

   debops config get --format toml views.system

Use :command:`jq` command to parse the DebOps configuration and extract path to
the Ansible inventory:

.. code-block:: shell

   debops config get --format json | jq .views.system.ansible.defaults.inventory

Perform the same operation as above, but let the :command:`debops` script do
the parsing by itself:

.. code-block:: shell

   debops config get --format json .views.system.ansible.defaults.inventory | jq .

The dot prefix (``.``) is optional.


:command:`debops config list`
-----------------------------

List all files which are parsed by the :command:`debops` script to configure
the runtime and project environment.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``<project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

Examples
~~~~~~~~

List currently parsed configuration files:

.. code-block:: shell

   debops config list


Configuration files
-------------------

DebOps uses multiple levels of configuration files that are merged together in
order of appearance:

- :file:`defaults.toml` (built-in default configuration)

- :file:`/usr/lib/debops/conf.d/` (configuration included by OS distribution
  maintainers)

- :file:`/usr/local/lib/debops/conf.d/` (configuration included by Python
  package maintainers)

- :file:`/etc/debops/conf.d/` (configuration defined by local system
  administrators)

- :file:`$XDG_CONFIG_HOME/debops/conf.d/` (per-user configuration)

- :file:`<project directory>/.debops.cfg` (per-project configuration file,
  legacy)

- :file:`<project directory>/.debops/conf.d/` (per-project configuration
  directory)

Configuration directories can contain JSON, TOML or YAML configuration files;
format is detected via the file extension (respectively :file:`*.json`,
:file:`*.toml`, :file:`*.yml` or :file:`*.yaml`). The configuration files are
interpreted in alphabetical order and their contents are merged together
recursively.


Environment files
-----------------

DebOps scripts support multiple configuration files which can be used to affect
its execution environment:

- :file:`/etc/default/debops` (per-system environment)

- :file:`$XDG_CONFIG_HOME/debops/environment` (per-user environment)

- :file:`<project directory>/.debops/environment` (per-project environment)

- :file:`<project directory>/.env` (per-project environment)

You can use these files to store environment variables which are then added to
the :command:`ansible-playbook` environment during playbook execution.

Environment files are compatible with the `python-dotenv`__ project. Each
environment variable is specified as:

.. code-block:: shell

   NAME=value

Empty lines and lines starting with the ``#`` character are ignored.

.. __: https://pypi.org/project/python-dotenv/
