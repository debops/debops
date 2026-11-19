.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _debops_configuration:

DebOps configuration
====================

DebOps stores its own options in a layered configuration tree: which
binaries to run, where to send journal messages, how project directories
behave. This page explains how the tree is built, how to read and change
it, and what happens when an option is wrong. The configuration system is
not the same thing as the :ref:`universal configuration
<universal_configuration>` syntax, which Ansible roles use for their
inventory variables.

.. contents::
   :depth: 3


How the configuration is built
------------------------------

DebOps merges several sources into one configuration tree. Later sources
override earlier ones:

- The packaged defaults, :file:`defaults.toml`. They define every option
  DebOps knows about, with a documented default for each.
- :file:`/usr/lib/debops/conf.d/` and :file:`/usr/local/lib/debops/conf.d/`.
  These directories hold configuration shipped by the OS distribution and
  by locally installed packages.
- :file:`/etc/debops/conf.d/`. The local system administrator's options.
- :file:`~/.config/debops/conf.d/`. Your own options, outside of any
  project.
- The project directory. Modern projects keep their configuration in
  :file:`.debops/conf.d/`, legacy projects in a :file:`.debops.cfg` file.
  See the :ref:`project_directory` guide for the directory layout.
- Environment overrides. A ``DEBOPS_CONFIG__SECTION__KEY`` variable
  overrides the option at the matching path of the tree. They rank above
  every file.

Within one directory, the files are read in alphabetical order and merged
together. A directory accepts files in TOML, JSON and YAML formats. The
format is detected from the file extension.

The merge is recursive. A section defined in several files keeps the
options of all of them. A list defined in several files combines the
entries of all of them. A value of a different type replaces the earlier
value.

Configuration values can reference environment variables, written as
``$VARIABLE`` or ``${VARIABLE}``. The references expand when the file is
loaded. Unknown references are left as they are written.

Infrastructure views add a second dimension. Each view of a project can
carry its own options in the ``views.<name>`` section of the tree. A
view can also have its own :file:`.env` file for local environment
variables.


Reading the effective configuration
-----------------------------------

The :command:`debops config get` command prints options of the merged
tree. Without arguments it prints the whole tree::

  alice@controller:~$ debops config get

An option is addressed by its dotted path::

  alice@controller:~$ debops config get syslog.level
  NOTICE

The output format comes from the ``config.default_output`` option; it
is ``yaml``. The ``-f``/``--format`` option switches the format for
one invocation. The ``unix`` format prints one option per line in the
dotted ``path=value`` notation, the same notation the environment
overrides use, with the list values comma-separated::

  alice@controller:~$ debops config get -f unix syslog
  syslog.address=/dev/log
  syslog.facility=user
  syslog.level=NOTICE
  syslog.port=514

The ``-k``/``--keys`` option lists the subkeys of an option instead of
its value; in the ``unix`` format the subkeys print as dotted paths.
The ``-r``/``--root`` option prints the option nested under its full
path, so the output shows where in the tree the option lives::

  alice@controller:~$ debops config get -r syslog.facility
  syslog:
    facility: user

When you need to know where a value comes from, add ``--show-origin`` or
``--show-scope``. Each option prints on one line: the source, the option
with its value joined by ``=``, and the columns separated by tabs::

  alice@controller:~$ debops config get --show-origin --show-scope syslog.level
  user	~/.config/debops/conf.d/99_config_set.json	syslog.level=DEBUG

The scope is the layer which last set the option: ``defaults``,
``system``, ``user``, ``project``, ``runtime`` or ``override``. The
origin is the source within that layer: a file path, an environment
variable name, or ``debops`` for the options which DebOps computes at
runtime. When a setting does not take effect, this output names the
winner. The ``debops config list`` command shows the same information
from the other side: the files and the overrides which were read.


Changing the configuration
--------------------------

The :command:`debops config set` command sets or removes options in the
configuration files. In a project directory, the options land in the
:file:`.debops/conf.d/99_config_set.json` file. Outside of one, they land
in your user configuration::

  alice@controller:~$ debops config set syslog.level DEBUG

The values are converted to the type of the option, so ``config set
syslog.port 514`` stores an integer. The ``-u``/``--user`` option sets
the option in the user configuration even inside a project.

An option which holds a list gains the values which the command gives
it. The values which the option already holds are skipped, so a
repeated command adds nothing::

  alice@controller:~$ debops config set -t list custom.tools ansible lxc
  alice@controller:~$ debops config set custom.tools tofu

An option which holds a single value takes one value and replaces the
old one. Several values to such an option are refused. The
``-t``/``--type`` option states the type of an option which DebOps
does not define, and creates an option with the empty value of the
type: ``list`` creates an empty list, ``int`` creates ``0``, ``str``
creates an empty string, ``dict`` creates an empty object. The option
must not be set yet; remove it first to change its type.

The ``-d``/``--delete`` option removes an option from the file. Given
values, it removes those values from a list option. The removal is
silent, and a value which another configuration layer still carries
is reported as a warning::

  alice@controller:~$ debops config set -d syslog.level

  alice@controller:~$ debops config set -d custom.tools lxc

The command manages files whose names end with
:file:`_config_set.json`. The numeric prefix of the file name decides
where the options rank among the files of that directory. When a file
with a different prefix exists, for example
:file:`50_config_set.json`, the command uses it instead of the default
one. This lets you choose the rank of the managed options by naming the
file, without specifying the file name on the command line.

Options unknown to DebOps are refused, with a pointer to the ``custom``
section described below.


Overriding options from the environment
---------------------------------------

Environment variables override the configuration files. The variable
name encodes the path of the option, with the path segments separated by
double underscores::

  alice@controller:~$ DEBOPS_CONFIG__SYSLOG__LEVEL=DEBUG debops run site.yml

The segments are matched case-insensitively. Keys which contain a hyphen,
like the Ansible binary names, keep it in the variable name. The shell
does not accept hyphens in variable assignments, so such overrides are
set through the :command:`env` command::

  alice@controller:~$ env DEBOPS_CONFIG__BINARIES__ANSIBLE=/opt/ansible/bin/ansible debops run site.yml

A value for a list option is a comma-separated string: ``a,b`` gives
the list with the values ``a`` and ``b``. A value which starts with
``[`` or ``{`` is parsed as JSON. To keep a comma inside one value,
give the value as a JSON string: ``'"a,b"'`` gives the string ``a,b``.

Overrides apply above every configuration file. They are meant for a
single invocation, a CI job or a container, not for permanent changes.
The :command:`debops config list` command lists the overrides which are
in effect.


Custom options
--------------

Scripts and integrations can store their own parameters in the DebOps
configuration tree. The ``custom`` section is reserved for them::

  custom:
    myscript:
      retries: 5

DebOps does not use this section and will not define options in it. The
options can be read with :command:`debops config get custom.myscript.retries`
and overridden with ``DEBOPS_CONFIG__CUSTOM__MYSCRIPT__RETRIES``.

Options which do not belong to DebOps and live outside of the ``custom``
section still work: they are reported as unknown and left in place. The
warning at the project level points to the ``custom`` section. Moving
the options there silences the warnings and protects them from colliding
with a DebOps option of the same name in a future release.


When the configuration is wrong
-------------------------------

The configuration is validated when it is loaded. The policy is
deliberately tolerant, with one exception:

- An option which DebOps does not know is reported as a warning and
  kept in the tree. Nothing in DebOps reads it, so keeping it breaks
  nothing.
- An option with a value of a wrong type is reported as a warning and
  dropped. The default value applies instead, because a wrong value
  could break the command which reads it.
- A configuration file which cannot be parsed is reported as a warning
  and skipped.

The :command:`debops config check` command turns these findings into an
exit code. It exits with a non-zero status when DebOps dropped an option
or skipped a file. That verdict makes the command usable in CI
pipelines::

  alice@controller:~$ debops config check
  The DebOps configuration is valid

The ``--strict`` option also fails the check on unknown options. Use it
in pipelines which should enforce a clean configuration.


Local environment files
-----------------------

DebOps composes the environment of the commands it runs from several
sources. The ambient environment of your shell wins over everything
below it:

- :file:`/etc/default/debops` and
  :file:`~/.config/debops/environment`, read on every run.
- :file:`.debops/environment` and :file:`.env` at the project root.
- :file:`.env` at the root of the infrastructure view,
  :file:`ansible/views/<view>/.env` in modern projects.

The files use the dotenv format. A ``PATH`` entry in them expands a
leading ``~`` to your home directory. The variables configure the
commands which DebOps runs. They are not available for ``${VARIABLE}``
expansion inside the configuration files: the files are loaded before
the view is known.

The :file:`.env` files are ignored by :command:`git` in newly created
projects. They hold the values which should stay local: tokens,
proxy settings, personal tool paths.


See also
--------

- :ref:`project_directory` for the layout of project directories
- :ref:`custom_environment` for the environment variables of Ansible
  roles
- The :command:`debops config` command help for the full option list
