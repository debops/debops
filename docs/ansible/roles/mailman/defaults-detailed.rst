.. Copyright (C) 2014-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.mailman`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _mailman__ref_core_configuration:

mailman__core_configuration
---------------------------

The ``mailman__core_*_configuration`` variables define the contents of the
:file:`/etc/mailman3/mailman.cfg` configuration file. You can read `Mailman
3 documentation`__ to find more about possible configuration options.

.. __: https://mailman.readthedocs.io/en/latest/src/mailman/config/docs/config.html

The same syntax is used in the ``mailman__hyperkitty_*_configuration``
variables to define the contents of the
:file:`/etc/mailman3/mailman-hyperkitty.cfg` configuration file.

Examples
~~~~~~~~

You can see the contents of the :envvar:`mailman__core_original_configuration`
for the default contents of the configuration file defined in YAML, and the
:envvar:`mailman__core_default_configuration` for the configuration options
changed from the defaults which are used by the role.

Syntax
~~~~~~

Each configuration option is defined as a YAML dictionary with specific parameters:

``name``
  Required. The name of the configuration file section. The entries with the
  same ``name`` parameter are merged together which can be used to modify
  already defined configuration entries from the Ansible inventory.

``state``
  Optional. Define the state of the configuration section. If not specified or
  ``present``, a given configuration section will be included in the generated
  configuration file. If ``absent``, the section will not be included in the
  configuration file.

  If the value is ``hidden``, the section will be included but its header
  (``[section]``) will not.

  If the value is ``ignore``, a given configuration entry will not be evaluated
  during role execution. This can be used to conditionally enable or disable
  features.

``separator``
  Optional, boolean. If defined and ``True``, the secion will have an
  additional empty line before it for cosmetic reasons.

``comment``
  Optional. A string or YAML text block with additional comments about a given
  configuration section.

``options``
  Optional. YAML list which contains the Mailman 3 configuration options in
  a given section. The ``options`` parameters from multiple configuration
  entries with the same ``name`` parameter are merged together; this can be
  used to modify the already defined configuration options from the Ansible
  inventory.

  Each configuration option is defined using a YAML dictionary with specific
  parameters:

  ``name``
    Required. The name of the configuration option. Entries with the same
    ``name`` are merged together which can be used to modify previously defined
    configuration options.

  ``option``
    Optional. If multiple variations of the same option are defined (for
    example a ``class`` database configuration option), they need to be defined
    in configuration entries with an unique ``name`` parameter. This however
    will be an issue in the actual configuration file.

    The ``option`` parameter can be used to specify the configuration option
    name to use instead of the ``name`` parameter.

  ``value``
    Required. The value which should be set for a given Mailman 3 configuration
    option. It can be a number, a string, a boolean or a YAML list of strings
    which will be joined together using spaces.

  ``comment``
    Optional. A string or YAML text block with a comment about a given
    configuration option.

  ``separator``
    Optional, boolean. If defined and ``True``, the option will have an
    additional empty line before it for cosmetic reasons.

  ``state``
    Optional. Define the state of a given configuration option. If not
    specified or ``present``, the option will be included in the configuration
    file. If ``absent``, the option will not be included in the configuration
    file. If ``ignore``, a given configuration entry will not be evaluated
    during role execution. If ``comment``, the option will be present in the
    configuration file, but commented out.


.. _mailman__ref_web_configuration:

mailman__web_configuration
--------------------------

The ``mailman__web_*_configuration`` variables define the contents of the
:file:`/etc/mailman3/mailman-web.py` configuration file.

Examples
~~~~~~~~

Change the randomly selected `Libravatar image generation engine`__ to one of:
``mm`` (simple avatar), ``identicon``, ``monsterid``, ``wavatar``, ``retro``,
``robohash``, ``pagan``:

.. __: https://wiki.libravatar.org/api/

.. code-block:: yaml

   mailman__web_configuration:

     - name: 'gravatar_default_image'
       value: 'identicon'

You can see the contents of the :envvar:`mailman__web_original_configuration`
for the default contents of the configuration file defined in YAML, and the
:envvar:`mailman__web_default_configuration` for the configuration options
changed from the defaults which are used by the role.

Syntax
~~~~~~

Each configuration option is defined as a YAML dictionary with specific parameters:

``name``
  Required. The name of the configuration option. Entries with the same
  ``name`` are merged together which can be used to modify previously defined
  configuration options.

``option``
  Optional. If multiple variations of the same option are defined (for
  example a ``databases`` database configuration option), they need to be defined
  in configuration entries with an unique ``name`` parameter. This however
  will be an issue in the actual configuration file.

  The ``option`` parameter can be used to specify the configuration option
  name to use instead of the ``name`` parameter.

``value``
  Optional. The value which should be set for a given Mailman 3 configuration
  option. It can be a number, a string, a boolean or a YAML list. More
  complicated values are defined using other parameters.

``options``
  Optional. YAML list which contains the Mailman 3 Web configuration options in
  a given section. The ``options`` parameters from multiple configuration
  entries with the same ``name`` parameter are merged together; this can be
  used to modify the already defined configuration options from the Ansible
  inventory.

  Each configuration option is defined using a string which is included as-is,
  or a YAML dictionary with specific parameters:

  ``name``
    The string to be included in the list. Entries with the same ``name`` are
    merged together which can be used to modify previously defined
    configuration options.

  ``comment``
    Optional. A string or YAML text block with a comment about a given
    configuration item.

  ``state``
    Optional. Define the state of a given configuration item. If not
    specified or ``present``, the item will be included in the configuration
    file. If ``absent``, the item will not be included in the configuration
    file. If ``ignore``, a given configuration entry will not be evaluated
    during role execution. If ``comment``, the item will be present in the
    configuration file, but commented out.

``type``
  Optional. Modify the value generated by the role:

  If the type is set to ``tuple``, the list defined in the ``value`` or
  ``options`` parameters will be rendered as a Python tuple.

  If the type is set to ``raw``, the ``value`` contents will be included as-is
  in the generated configuration file. This can be used to include small
  snippets of Python code specified as strings.

``config``
  Optional. YAML dictionary with the configuration rendered in the final file
  using the ``to_nice_json`` Ansible filter. This parameter can be used to
  define dictionary-based configuration options. The ``config`` parameters from
  configuration entries with the same ``name`` parameter replace each other in
  order of appearance.

``raw``
  Optional. String or YAML text block which will be included in the generated
  configuration file as-is. This can be used to include Python code in the
  generated configuration file that cannot be expressed otherwise.

``comment``
  Optional. A string or YAML text block with a comment about a given
  configuration option.

``separator``
  Optional, boolean. If defined and ``True``, the option will have an
  additional empty line before it for cosmetic reasons.

``state``
  Optional. Define the state of a given configuration option. If not
  specified or ``present``, the option will be included in the configuration
  file. If ``absent``, the option will not be included in the configuration
  file. If ``ignore``, a given configuration entry will not be evaluated
  during role execution. If ``comment``, the option will be present in the
  configuration file, but commented out.

``copy_id_from``
  Optional. Specify the ``name`` parameter of a different configuration option;
  the configuration entry with this parameter will copy the internal "id" value
  of the specified configuration entry. This can be used to reorder
  configuration entries in the finial generated configuration file.

``weight``
  Optional. Positive or negative number which can be used to affect the
  position of a given configuration option in the generated file. Specifying
  a positive number will lower the option within the file (more weight),
  specifying a negative number will raise the option (less weight). This can be
  used to reorder configuration entries in the finial generated configuration
  file.


.. _mailman__ref_templates:

mailman__templates
------------------

The ``mailman__*_templates`` variables can be used to define `Mailman
3 templates`__ stored in the filesystem. The files will be stored in
subdirectories under :file:`/var/lib/mailman3/templates/` directory and can be
used change how Mailman processes mailing list messages.

.. __: https://mailman.readthedocs.io/en/stable/src/mailman/rest/docs/templates.html

Examples
~~~~~~~~

Remove the default message footer in all lists (this is enabled by default):

.. code-block:: yaml

   mailman__templates:

     - name: 'site/en/list:member:generic:footer.txt'
       content: ''

Syntax
~~~~~~

Each template is defined by a YAML dictionary with specific parameters:

``name``
  Required. A path relative to the :file:`/var/lib/mailman3/templates/`
  directory with the template filename, ending with ``.txt`` extension. Any
  subdirectories will be created automatically, if not present. Configuration
  entries with the same ``name`` parameter are merged together in order of
  appearance.

``state``
  Optional. If not specified or ``present``, the template file will be
  generated. If ``absent``, the template file will be removed.

``content``
  Optional. String or YAML text block with contents of the generated template.
  If not specified, the template will be empty.
