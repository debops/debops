.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.resolvconf`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _resolvconf__ref_interface_order:

resolvconf__interface_order
---------------------------

The ``resolvconf__*_interface_order`` variables define the contents of the
:file:`/etc/resolvconf/interface-order` configuration file - see the
:man:`interface-order(5)` manual page for details about this file.

Examples
~~~~~~~~

See the :envvar:`resolvconf__original_interface_order` default variable to see
the original contents of the configuration file represented in the role. The
:envvar:`resolvconf__default_interface_order` variable contains the
modifications to the original configuration file defined in the role by default
and enabled conditionally.

Syntax
~~~~~~

The contents of the ``resolvconf__*_interface_order`` variables are a list of
YAML dictionaries, each dictionary defines a section of the configuration file
using specific parameters:

``name``
  Required. A name of a given section, used only as a handle for a given
  configuration entry. Multiple entries with the same ``name`` parameter are
  merged together and can affect a given entry in order of appearance.

``value``
  Required. A string or a YAML text block which will be inserted in the
  generated configuration file. See the :man:`interface-order(5)` for details
  about what can be defined here.

``comment``
  Optional. A string or YAML text block with additional comments about a given
  configuration entry.

``state``
  Optional. If not specified or ``present``, a given configuration section will
  be included in the generated configuration file. If ``absent``,
  a configuration section will be removed from the generated configuration
  file. If ``ignore``, a given configuration entry will not be evaluated by the
  role during its execution.

``anchor_to``
  Optional. Name of another configuration entry (its ``name`` parameter) to
  anchor this entry to. The entry is placed right after the anchor when its
  ``weight`` is zero or positive, and right before it when ``weight`` is
  negative. Anchoring takes precedence over zone-based placement. See
  :ref:`universal_configuration_advanced_weight` for details.

``weight``
  Optional. A positive or negative number which selects the placement zone of
  a given entry relative to other configuration entries: negative values move
  it to the top, ``0`` (the default) keeps it in the middle in source order,
  and positive values move it to the bottom. The magnitude of the value does
  not matter; use ``anchor_to`` for ordering relative to a specific entry. See
  :ref:`universal_configuration_advanced_weight` for details.
