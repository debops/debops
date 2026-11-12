.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _configuration_options:

Adding a configuration option
=============================

The DebOps configuration tree is validated against a JSON Schema, and
its documented surface is the packaged defaults. Adding an option means
touching both, and a few rules keep the two from drifting apart. This
page is the checklist for that work.

.. contents::
   :depth: 2


Define the default
------------------

Every option starts in :file:`src/debops/_data/defaults.toml`, with a
comment above it which explains what the option does and what happens
when it is not set. The defaults are the documentation of the option's
existence. A reader who runs :command:`debops config get` sees them.

The defaults file is rendered as a Jinja template, so a default can be
computed from the environment:

.. code-block:: toml

   # The command used to run the 'diff' tool.
   diff = "{{ env['DEBOPS_CMD_DIFF'] | d('diff') }}"

Keep this ability for options which genuinely depend on the host. A
static option is a plain TOML value.


Define the type
---------------

The schema in :file:`src/debops/_data/debops/config/schema.json` is the
type definition of the tree. An option without a schema entry is
invisible to the schema. The validation reports it as unknown, the
environment overrides refuse it, and :command:`debops config set`
refuses it.

Add the option to its section, with its type:

.. code-block:: json

   "port": {
     "type": "integer"
   }

A value which only accepts a fixed set of words gets an ``enum``. The
``facility`` and ``level`` options of the ``syslog`` section show the
pattern. The enum values must match the values the code accepts, not
the values the code would tolerate.


Mirror the code's tolerance
---------------------------

The schema must not be stricter than the code. When the code accepts a
quoted value because quoting is an easy mistake in YAML, the schema
accepts it too:

.. code-block:: json

   "version": {"type": ["integer", "string"]}

The rule has a direction: the schema describes what the code *accepts*,
not what the defaults *use*. An option the code reads with
:command:`strtobool` is ``["boolean", "string"]`` in the schema. An
option the code uses as an integer without conversion is a plain
``integer``. A quoted value for such an option is a user mistake worth
a warning.


Remember what the templates write
---------------------------------

The schema's source of truth is everything which can appear in the
tree, not only what the Python code reads. The project templates write
options of their own. :command:`debops project init` writes the
``override_paths`` section into every new project, and a schema without
that section reports each of those projects as carrying an unknown
option.

An option which a template writes, or a section which a Collection
plugin reads, belongs in the schema from the same change. The consumer
sweep for a new option includes the templates and the Collection
plugins, not only the Python sources.


Mind the namespace
------------------

The fixed sections of the tree are closed to unknown options. A new
option joins an existing section, or it defines a new root section. A
new root section takes a name which nothing else uses, now or plausibly
later. The ``custom`` section is reserved for options defined outside
of DebOps and is not available.

The scope and origin labels rendered by
:command:`debops config get --show-origin` are single tokens. A new
runtime layer which records an origin labels it without spaces, so the
output stays splittable.


Check the pin
-------------

The unit suite pins the packaged defaults against the schema. After the
two edits, the defaults test must stay green. It fails when an option
exists in one file and not in the other. Run it before you commit:

.. code-block:: console

   alice@controller:~/src/debops (master) $ make unit


Document the option
-------------------

An option which users are meant to set belongs in the documentation.
The user guide explains the behavior. The :command:`debops config`
manual page documents the commands. An option which only the templates
or the code set does not need user documentation. Its comment in
:file:`defaults.toml` should still say what it does.


See also
--------

- :ref:`debops_configuration` for how the configuration system works
- :ref:`configuration_recipes` for practical uses of the system
