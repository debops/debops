.. Copyright (C) 2016-2018 Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2016-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.roundcube`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _roundcube__ref_configuration:

roundcube__configuration
------------------------

The ``roundcube__*_configuration`` variables define the contents of the
:file:`config/config.php.inc` configuration file located in the Roundcube
installation directory. The contents are defined using YAML data structures and
converted to PHP via the role template.

Examples
~~~~~~~~

Define a few configuration options with simple syntax:

.. code-block:: yaml

   roundcube__configuration:

     - string_option: 'string value'

     - number_option: 1234

     - bool_true_option: True

     - bool_false_option: False

     - null_option: null

     - empty_array: []

     - empty_string: ''

     - simple_list: [ 'item1', 'item2', 'item3' ]

Define a few configuration options with more advanced syntax which allows for
conditions and better control over values:

.. code-block:: yaml

   roundcube__configuration:

     - name: 'string_option'
       value: 'string value'

     - name: 'number_option'
       value: 1234

     - name: 'bool_true_option'
       value: True

     - name: 'bool_false_option'
       value: False

     - name: 'null_option'
       value: null

     - name: 'empty_array'
       value: []

     - name: 'empty_string'
       value: ''

     - name: 'simple_list'
       value: [ 'item1', 'item2, 'item3' ]

     - name: 'option_with_constant'
       value: "'string' . CONSTANT . 'other-string'"
       quotes: False

Insert raw PHP code in the configuration file:

.. code-block:: yaml

   roundcube__configuration:

     - name: 'custom_code'
       raw: |
         if( isset( $_SERVER['MACHINE_NAME'] )) {
             $config['syslog_facility'] = LOG_USER;
         }

Add a multi-level option in the configuration (in a "sub-array"):

.. code-block:: yaml

   roundcube__configuration:

     - name: 'multi_level_option'
       option: [ 'firstlevel', 'secondlevel' ]
       value: True

Create complex PHP ``array()`` definitions parsed directly in the template:

.. code-block:: yaml

   roundcube__configuration:

     - name: 'spellcheck_languages'
       array:
         - de: 'Deutsch'
         - en: 'English'
         - pl: 'Polish'

     - name: 'compose_responses_static'
       array:
         - [ 'name': 'Canned Response 1', 'text': 'Static Response One' ]
         - [ 'name': 'Canned Response 2', 'text': 'Static Response Two' ]

You can see more examples in the :envvar:`roundcube__original_configuration`
and the :envvar:`roundcube__default_configuration` variables.

Syntax
~~~~~~

The Roundcube configuration options can be defined using a simple or expanded
syntax. Simple syntax uses YAML dictionary keys as the configuration option
names (the ``name`` equivalent), and dictionary values as the option values
(the ``value`` equivalent). In this case, only one YAML dictionary key/value
pair should be defined at a time.

The expanded definition is enabled when a given configuration entry contains
the ``name`` parameter and uses a set of parameters for better control over
the final output:

``name``
  Required. Roundcube configuration option name. Configuration entries with the
  same ``name`` parameter are merged in order of appearance; this can be used
  to change configuration options conditionally.

  If the ``option`` parameter is specified, the ``name`` parameter is not used
  as the configuration option name.

``value``
  Optional. The value of the Roundcube configuration option. It can be
  specified as a string, a YAML list, ``True`` or ``False`` boolean, a ``null``
  value, a positive or negative number. if the ``value`` parameter is not
  specified, the result will be an empty list (``array()`` in PHP).

  The ``value`` parameters from multiple configuration entries override each
  other, with exception of YAML lists - the lists are additive and the result
  will contain only unique values. Only strings are supported in lists.

``array``
  Optional. Define a `PHP array()`__ data structure using YAML. The ``array``
  parameter is used only when the ``value`` or ``raw`` parameters are not
  present. The ``array`` parameters from multiple configuration entries
  override each other. See varius examples in the role default variables for
  better idea on how to define the data structures.

  .. __: https://www.php.net/manual/en/language.types.array.php

``raw``
  Optional. String or YAML text block with PHP code, which will be included in
  the generated configuration file "as is". If the ``raw`` parameter is
  defined, it takes precedence over ``value`` or ``array`` parameters.

``option``
  Optional. It can be a string or a YAML list of strings. If defined, the value
  will be used instead of the ``name`` parameter as the Roundcube configuration
  option name. If a list is defined, each list element will be used as
  a "subkey", for example ``[ 'one', 'two' ]`` value would become
  ``$config['one']['two']`` in the generated configuration file.

``quotes``
  Optional, bollean. If defined and ``False``, the quotes around the string
  value will not be included in the generated configuration file. This can be
  used to create values which contain PHP constants; the text strings in the
  values need to be additionally quoted in this case.

``state``
  Optional. If not specified or ``present``, a given Roundcube option will be
  present in the configuration file. If ``absent``, a given option will be
  removed from the configuration file (or not included if not present).
  If ``init``, the configuration option will be prepared, but will not be
  active and won't show up on the generated configuration file - this can be
  used to prepare configuration that will be activated conditionally in another
  configuration entry. If ``ignore``, a given configuration entry will not be
  evaluated during role execution. If ``comment``, a given Roundcube
  configuration option will be present in the generated file, but commented
  out.

``comment``
  Optional. String or YAML text block with comments about a given configuration
  option.

``separator``
  Optional, boolean. If defined and ``True``, the role will add an empty line
  before a given configuration option, to allow for better readability.

``section``
  Optional. Specify the configuration file section name to put a given
  configuration option into. Section names are defined using the
  :ref:`roundcube__ref_configuration_sections` variables. If not defined, the
  configuration option will be put into the ``unknown`` section.

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


.. _roundcube__ref_configuration_sections:

roundcube__configuration_sections
---------------------------------

The ``roundcube__*_configuration_sections`` variables define what sections are
present in the :file:`config/config.inc.php` configuration file. Using these
variables, the sections can be reordered and modified as needed.

Examples
~~~~~~~~

See the :envvar:`roundcube__default_configuration_sections` variable for the
list of the sections defined by default.

Syntax
~~~~~~

Configuration sections are defined using a list of YAML dictionaries, each
dictionary uses specific parameters:

``name``
  Required. Name of a given section, used also as its identificator in the main
  configuration ``section`` parameter. Multiple configuration entries with the
  same ``name`` are merged together.

``title``
  Optional. Set a custom title for a given section. If not specified, the
  ``name`` parameter will be used as the title.

``state``
  Optional. If not specified or ``present``, a given section will be present in
  the generated configuration file. If ``absent``, a given section will be
  removed from the configuration file. if ``hidden``, the section will be
  present, but the title will not be included in the generated configuration
  file. if ``ignore``, a given configuration entry will not be evaluated during
  role execution.


.. _roundcube__ref_plugins:

roundcube__plugins
------------------

The ``roundcube__*_plugins`` lists define what plugins will be enabled in
Roundcube and optionally installed from the `Roundcube Plugins repository`__
using `PHP Composer`__. The :command:`composer` command is assumed to be
installed by the :ref:`debops.php` role.

.. __: https://plugins.roundcube.net

.. __: https://getcomposer.org

Examples
~~~~~~~~

Override the default value in the ``cloud_button`` plugin configuration file:

.. code-block:: yaml

   roundcube__plugins:

     - name: 'cloud_button'
       state: 'append'
       options:

         - cloud_button_url: 'https://cloud.example.org/'

See the :envvar:`roundcube__default_plugins` for a list of Roundcube plugin
definitions which are enabled by the role.

Syntax
~~~~~~

The plugins are defined using YAML dictionaries with specific parameters:

``name``
  Required. The name of the plugin, also the directory name in the
  :file:`plugins/` subdirectory where the plugin is located. The ``name``
  parameter is used in the ``$config['plugins']`` configuration option to
  enable the plugin, only if the ``state`` parameter is set to ``enabled``.
  Multiple configuration entries with the same ``name`` parameter are merged
  together in the order of appearance.

``state``
  Optional. If not defined or ``present``, the plugin will be installed (if the
  ``package`` parameter is also defined), and its :file:`config.inc.php`
  configuration file will be generated, but the plugin itself will not be
  active in Roundcube. If ``enabled``, the plugin will be installed if needed,
  and will be activated in the Roundcube configuration file.

  If ``absent``, the plugin will be deactivated, but it will not be uninstalled
  from the host. If ``ignore``, a given configuration entry won't be evaluated
  during role execution. If ``init``, a given configuration entry will be
  prepared but will not be activated - this can be used to prepare
  configuration for plugins and activate them later conditionally if needed.
  If ``append``, a given configuration entry is evaluated by the role only if
  an entry with the same name is already present in the configuration (was
  defined previously).

``package``
  Optional. If specified, a given plugin will be installed using PHP Composer
  from the `Roundcube Plugins`__ repository. You need to specify the plugin name
  using the ``namespace/plugin`` format, plugin names can be found on the
  repository page.

  .. __: https://plugins.roundcube.net/

  This parameter is passed to the ``composer`` Ansible module as the
  ``arguments`` parameter. You can use any valid value, for example by setting
  a specific version of a plugin to use by defining it as
  ``namespace/plugin:version``.

``options``
  Optional. List of configuration options for a specific plugin which will be
  stored in the :file:`plugins/<plugin_name>/config.inc.php` configuration
  file. The list format is the same as the Roundcube global configuration
  defined in the :ref:`roundcube__ref_configuration` variables.
