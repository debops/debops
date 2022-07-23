.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.miniflux`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _miniflux__ref_configuration:

miniflux__configuration
-----------------------

The ``miniflux__*_configuration`` variables define the contents of the
:file:`/etc/miniflux.conf` configuration file. You can find information about
available configuration options `in Miniflux online documentation`__.

.. __: https://miniflux.app/docs/configuration.html

The role uses :ref:`universal_configuration` system to integrate the default
and inventory variables during configuration file generation.

Examples
~~~~~~~~

You can see the default configuration defined in the role in
:envvar:`miniflux__default_configuration` variable to see examples of various
configuration options.

Syntax
~~~~~~

The variables are defined as lists of YAML dictionaries, each entry defines
a configuration option using specific parameters:

``name``
  Required. Name of the variable to define in the configuration file,
  automatically converted to uppercase. Configuration entries with the same
  ``name`` parameter are merged together and can affect each other.

``comment``
  Optional. String or YAML text block with a comment about a given
  configuration option.

``value``
  The value of a given configuration option. It can be a string, a number,
  a boolean variable or a YAML list which will be converted to strings
  separated by space.

``raw``
  If the ``raw`` parameter is specified, the ``name`` and ``value`` parameters
  are not included in the generated configuration file. The contents of the
  ``raw`` parameter (string or YAML text block) will be included in the
  generated configuration file as-is. You can use Jinja inside of the ``raw``
  parameter to augment generated configuration as needed.

``state``
  Optional. If not specified or ``present``, a given configuration option will
  be included in the generated file. If ``absent``, a given configuration
  option will not be included in the finished file. If ``comment``, the option
  will be included but commented out. If ``ignore``, a given configuration
  entry will not be evaluated during role execution.

``separator``
  Optional. Add an empty line before a given configuration option, for
  aesthetic purposes.
