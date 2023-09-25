.. Copyright (C) 2021-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

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

``-k, --keys``
  Instead of returning the entire configuration tree, return a list of
  configuration keys present at a given configuration level. Empty output or
  list means that there are no more subkeys present at a given level.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

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

List known infrastructure views in a given project directory:

.. code-block:: shell

   debops config get -k views

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

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

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

Values of configuration options can contain environment variables specified as
``$VARIABLE`` or ``${VARIABLE}`` strings. These variables will be expanded at
runtime and can be used to augment the final configuration. Variables
themselves can be defined in the :file:`<project directory>/.debops/environment`
or the :file:`<project directory>/.env` files and they will be automatically
incorporated into runtime environment. Users can use the :ref:`cmd_debops-env`
command to inspect the runtime environment variables.
