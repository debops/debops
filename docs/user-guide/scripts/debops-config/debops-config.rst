.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops config`
------------------------

Display the configuration information about a DebOps project. Configuration is
gathered from multiple places and merged together. The default display format
is TOML and can be changed to JSON to allow parsing.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``--env``
  Display the current environment variables which will be used by DebOps and
  passed to Ansible during its execution. This can be used to check if the
  environment variables configured in various files are correctly initialized.

``--format json|toml``
  Specify the format of the output. The default format is TOML which is
  considered human-friendly. The JSON format can be used to enable easy parsing
  by programs.

Examples
~~~~~~~~

Use :command:`jq` command to parse the DebOps configuration and extract path to
the Ansible inventory:

.. code-block:: shell

   debops config --format json | jq .views.system.ansible.defaults.inventory


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

Configuration directories can contain YAML, TOML and JSON configuration files;
format is detected via the file extension (respectively :file:`.yml` or
:file:`.yaml`, :file:`.toml` or :file:`.json`). You can find more details about
the contents of the configuration files and overall configuration structure in
the :ref:`debops config <cmd_debops-config>` command documentation.


Environment files
-----------------

DebOps scripts support multiple configuration files which can be used to affect
its execution environment:

- :file:`/etc/default/debops` (per-system environment)

- :file:`$XDG_CONFIG_HOME/debops/environment` (per-user environment)

- :file:`<project directory>/.env` (per-project environment)

You can use these files to store environment variables which are then added to
the :command:`ansible-playbook` environment during playbook execution.

Each environment variable is specified as:

.. code-block:: shell

   NAME=value

Empty lines and lines starting with the ``#`` character are ignored.
