Default variable details
========================

Some of ``debops.resolvconf`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

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

``copy_id_from``
  Optional. Name of a configuration entry (its ``name`` parameter) from which
  a given entry should copy its internal "id" value. This can be used to rougly
  place a given configuration entry near the specified configuration section
  without the need to modify the order of all of the other entries.

``weight``
  Optional. A positive or negative number which defines an additional "weight"
  of a given entry relative to other configuration entries. This parameter can
  be used to fine-tune the order of the configuration sections in the generated
  configuration file.
