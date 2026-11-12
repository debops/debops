.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _configuration_recipes:

Configuration recipes
=====================

These recipes show practical uses of the DebOps configuration system in
the daily work of a system administrator. They cover the shell, CI
pipelines and your own scripts. The :ref:`DebOps configuration
<debops_configuration>` guide explains how the system works. This page
assumes that explanation and shows what to do with it.

.. contents::
   :depth: 2


Debug a setting that does not take effect
-----------------------------------------

A layered configuration has one classic problem: you set an option, and
the system behaves as if you did not. Something else sets the option
after you, or before you see it. The ``--show-origin`` option names the
winner::

  alice@controller:~$ debops config get --show-origin --show-scope syslog.level
  override	DEBOPS_CONFIG__SYSLOG__LEVEL	syslog.level=DEBUG

The scope tells you which layer won: a file, the packaged defaults, the
runtime state of the project, or an environment override. In this
example an environment variable set the option, and no file edit will
change it. Remove the variable, or work with it.

The same query works for a whole section. Each option prints on its own
line, attributed to its own source::

  alice@controller:~$ debops config get --show-origin syslog
  ~/.config/debops/conf.d/99_config_set.json	syslog.facility=local1
  /usr/share/debops/defaults.toml	syslog.level=NOTICE


Set one option across all projects
----------------------------------

Project configuration files live inside each project. An option which
should be the same everywhere belongs one level up, in your user
configuration::

  alice@controller:~$ debops config set -u version_check.enabled true
  Set 'version_check.enabled' to 'true' in /home/alice/.config/debops/conf.d/99_config_set.json

The ``-u``/``--user`` option writes to
:file:`~/.config/debops/conf.d/`, which every project reads. The option
applies everywhere, and each project can still override it in its own
files.


Validate the configuration in CI
--------------------------------

A mistake in a configuration file is reported as a warning, and a
wrongly typed option falls back to its default. That is the right
behavior for a person running a command. A CI pipeline should refuse the
mistake instead::

  alice@controller:~$ debops config check
  The DebOps configuration is valid

The command exits with a non-zero status when DebOps dropped an option
or skipped a file. The ``--strict`` option also fails the check on
unknown options, which catches typos in option names before they reach
production::

  alice@controller:~$ debops config check --strict


Override options for a single run
---------------------------------

Some changes should not be written anywhere: a debug level for one run,
a different Ansible binary in a container, a test value in CI. The
environment does this without touching any file::

  alice@controller:~$ DEBOPS_CONFIG__SYSLOG__LEVEL=DEBUG debops run site.yml

The variable name encodes the path of the option. The value is converted
to the type of the option, and the override ranks above every file. For
a container image which cannot carry project files, the overrides are
the configuration interface. Set the ``DEBOPS_CONFIG__*`` variables in
the environment and keep the image generic.


Keep local values out of git
----------------------------

A project directory is usually a :command:`git` repository, and its
configuration is committed. Values which should stay local, like tokens
or proxy credentials, belong in the :file:`.env` files, which git
ignores:

.. code-block:: text

   # .env at the project root
   https_proxy='http://proxy.example.com:3128'
   mytool_token='s3cret-token'

A modern project can also carry a :file:`.env` file per infrastructure
view, in :file:`ansible/views/<view>/.env`. The view's file wins over
the project's, and your shell environment wins over both. Use the view
file for values which only make sense in one view, for example a
staging-only mirror address.


Read the configuration from a Python script
-------------------------------------------

The configuration system is a Python library. A script which runs on a
host with DebOps installed can read the effective configuration
directly:

.. code-block:: python

   from debops.core.config import Configuration

   config = Configuration()
   print(config.config_get('syslog.level'))

Without arguments, the object is the DebOps configuration: the same
layers, in the same order, that the :command:`debops` command uses. The
``Configuration`` object offers more: the ``config_origins()`` method
returns the source of each option, and ``apply_env_overrides()``
applies the environment the same way the command does.


Build your own tool on the configuration machinery
--------------------------------------------------

The same machinery can drive a configuration which has nothing to do
with DebOps. Pass the sources you want, and the constructor builds a
standalone configuration with the same semantics: layered merge,
``${VARIABLE}`` expansion, schema validation and typed values.

.. code-block:: python

   from debops.core.config import Configuration

   config = Configuration(
       defaults='defaults.toml',
       paths=[('/etc/mytool/conf.d', 'system'),
              ('~/.config/mytool/conf.d', 'user')],
       schema='schema.json',
       env_prefix='MYTOOL_CONFIG__',
       env_files=['/etc/default/mytool'])

   port = config.config_get('server.port')
   config.config_set('server.port', 9090)

The defaults file is rendered as a Jinja template before it is parsed,
so the defaults can be computed from the environment. The schema is a
plain JSON Schema file. It defines which options exist and of which
type, and the validation and the type conversion are driven by it. The
environment overrides follow the same rule as in DebOps:
``MYTOOL_CONFIG__SERVER__PORT`` overrides the ``server.port`` option.

This recipe fits a tool which grows past a single configuration file.
The signs: several sources with real precedence, an option vocabulary
validated against a schema, and values typed at load time. When the
tool needs less, the standard library modules are the better choice.


See also
--------

- :ref:`debops_configuration` for how the configuration system works
- :ref:`project_directory` for the project directory layout
