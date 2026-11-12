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
  Specify the format of the output. The default format is 'unix' which is
  considered human-friendly. The JSON format can be used to enable easy parsing
  by programs.

``-k, --keys``
  Instead of returning the entire configuration tree, return a list of
  configuration keys present at a given configuration level. Empty output or
  list means that there are no more subkeys present at a given level.

``-r, --root``
  Print the option nested under its full path from the root of the
  configuration tree, which shows where in the tree the option is defined.

``--show-origin``
  Print the options as plain text, one line per option: the source
  which last set each option, then the option and its value joined by
  ``=``. The source is the configuration file which set the option,
  the environment variable for the options overridden from the
  environment, or ``debops`` for the options which the tool computes
  at runtime. Paths under the home directory are shown with ``~``.
  The columns are separated by tabs and contain no whitespace
  themselves, so the lines can be split on tabs reliably. This
  rendering cannot be combined with other output formats or options.

``--show-scope``
  Print the options as plain text, one line per option: the
  configuration layer which last set each option (one of ``defaults``,
  ``system``, ``user``, ``project``, ``runtime`` or ``override``),
  then the option and its value joined by ``=``. When combined with
  ``--show-origin``, the scope column comes first.

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


:command:`debops config set`
----------------------------

Set or remove DebOps configuration options in the configuration files. In a
project directory, the options are managed in the
:file:`.debops/conf.d/99_config_set.json` file of the project; outside of one,
in the user's configuration directory. The values are converted to the type of
the option as defined by DebOps.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``-u, --user``
  Set the option in the user configuration
  (:file:`$XDG_CONFIG_HOME/debops/conf.d/`) instead of the project
  configuration.

``-d, --delete``
  Remove the option from the configuration file instead of setting it.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``key``
  Path of the configuration option in the configuration tree, with subkeys
  specified using dot (``.``) as a separator.

``value``
  The value to set the option to. The value is converted to the type of the
  option: integers, booleans and lists are recognized for the options which
  DebOps defines, other options are parsed as JSON when they look like JSON
  and stored as strings otherwise. Custom options can be defined under the
  ``custom`` section of the configuration tree, which DebOps reserves for
  options defined outside of DebOps.

Examples
~~~~~~~~

Change the syslog facility used by the :command:`debops` command:

.. code-block:: shell

   debops config set syslog.facility local1

Define a custom option used by an external script:

.. code-block:: shell

   debops config set custom.myscript.retries 5

Remove an option from the configuration file:

.. code-block:: shell

   debops config set -d custom.myscript.retries

The :command:`debops config set` command manages the files whose names end
with :file:`_config_set.json`. When a file with a different numeric prefix
exists in the target directory, for example :file:`50_config_set.json`, it is
used instead of the default one, so the prefix decides where the managed
options rank among the configuration files of the directory.


:command:`debops config check`
------------------------------

Check the DebOps configuration for errors: unknown options, options with
values of a wrong type, configuration files which cannot be parsed. The
command exits with a non-zero status when the configuration was modified by
the check: an option was dropped, or a file could not be parsed. This makes
the command usable in CI pipelines, before the configuration is deployed.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``--strict``
  Report unknown configuration options as errors as well, not only the
  options which the check drops.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

Examples
~~~~~~~~

Check the configuration of the current project directory:

.. code-block:: shell

   debops config check


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
