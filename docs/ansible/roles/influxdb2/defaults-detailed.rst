.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.influxdb2`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _influxdb2__ref_configuration:

influxdb2__configuration
------------------------

The ``influxdb2__*_configuration`` variables control the contents of the
:file:`/etc/influxdb/config.toml` configuration file. The role uses
:ref:`universal_configuration` system to define InfluxDBv2 options.

Examples
~~~~~~~~

The default configuration can be found in the
:envvar:`influxdb2__default_configuration` variable.

Syntax
~~~~~~

Configuration is defined using a list of YAML dictionaries, each dictionary
defines a single configuration entry using specific parameters:

``name``
  Required. Name of the "configuration section", not used otherwise. Entries
  with the same ``name`` parameter are merged in order of appearance and can
  affect each other.

``config``
  Required. YAML dictionary with InfluxDB v2 configuration options. The
  ``config`` parameters from all entries are merged recursively in order of
  appearance in the finished configuration file.

``state``
  Optional. If not specified or ``present``, a given configuration entry will
  be included in the finished configuration file. If ``absent``, the
  configuration entries will not be included in the generated file. If
  ``ignore``, a given configuration entry will be ignored during role
  execution.
