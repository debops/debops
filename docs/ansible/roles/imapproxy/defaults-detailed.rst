.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.imapproxy`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _imapproxy__ref_configuration:

imapproxy__configuration
------------------------

The ``imapproxy__*_configuration`` variables define the contents of the
:file:`/etc/imapproxy.conf` configuration file. The contents are defined
using YAML data structures and converted to a valid configuration file via
the role template.

The ``imapproxy__*_configuration`` variables are implemented using the
:ref:`universal configuration <universal_configuration>` syntax.

:file:`/etc/imapproxy.conf` is a simple configuration file which contains
configuration parameters in a `key value` syntax (note: *not* `key = value`),
meaning that the universal configuration variables are also a simple list of
`name` and `value` parameters which end up as `key value` in
:file:`/etc/imapproxy.conf`.

:envvar:`imapproxy__default_configuration` already contains a list of all the
configuration parameters which are supported by imapproxy and may appear in
:file:`/etc/imapproxy.conf` together with comments documenting the parameters.

If you need to override any parameter, you can do so by changing
:envvar:`imapproxy__configuration`, :envvar:`imapproxy__group_configuration` or
:envvar:`imapproxy__host_configuration` according to your needs.

Examples
~~~~~~~~

Changing a couple of configuration options:

.. code-block:: yaml

   imapproxy__configuration:

     - name: 'dns_rr'
       value: 'yes'
       state: 'present'

     - name: 'chroot_directory'
       state: 'comment'

You can see more examples in the :envvar:`imapproxy__default_configuration`
variable.

Syntax
~~~~~~

The imapproxy configuration options can be configured using a number of
configuration entries, each containing a ``name`` parameter and a number
of additional parameters (see the example above).

Supported parameters are:

``name``
  Required. imapproxy configuration option name. Configuration entries with the
  same ``name`` parameter are merged in order of appearance; this can be used
  to change configuration options conditionally.

  If the ``option`` parameter is specified, it is used instead of the ``name``
  parameter as the key value in the generated configuration file.

``value``
  Optional. The value of the imapproxy configuration option. It can be
  specified as a string, a YAML list, ``True`` or ``False`` boolean, a ``null``
  value, a positive or negative number. if the ``value`` parameter is not
  specified, the result will be empty.

  The ``value`` parameters from multiple configuration entries override each
  other.

``raw``
  Optional. String or YAML text block with text which will be included in
  the generated configuration file "as is". If the ``raw`` parameter is
  defined, it takes precedence over ``value`` parameter.

``state``
  Optional. If not specified or ``present``, a given imapproxy option will be
  present in the configuration file. If ``absent``, a given option will be
  removed from the configuration file (or not included if not present).
  If ``init``, the configuration option will be prepared, but will not be
  active and won't show up on the generated configuration file - this can be
  used to prepare configuration that will be activated conditionally in another
  configuration entry. If ``ignore``, a given configuration entry will not be
  evaluated during role execution. If ``comment``, a given imapproxy
  configuration option will be present in the generated file, but commented
  out.

``comment``
  Optional. String or YAML text block with comments about a given configuration
  option.

``copy_id_from``
  Optional. Copy the internal "id" of a configuration option specified by the
  ``name`` parameter to the current configuration option. This parameter can be
  used to reorder configuration options relative to a specific option.

``weight``
  Optional. Positive or negative number which defines the additional "weight"
  of an option. Smaller or negative weight will move the option higher in the
  configuration file, Bigger weight will move the configuration option lower in
  the configuration file.

``value_cast``
  Optional. Specify the type of a given value to use in the configuration file.
  Supported types: ``int``/``integer``, ``str``/``string``, ``float``,
  ``null``/``none``, ``bool``/``boolean``. This parameter is onlu useful when
  the value is defined using another variable, in which case the type
  information is not preserved by Jinja templating.
