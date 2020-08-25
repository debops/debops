.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:
      :depth: 1

Usage as a role dependency
--------------------------

To use the custom Ansible plugins from this role in your own Ansible roles, you
should include the ``ansible_plugins`` role as a dependency, in
:file:`meta/main.yml` file of a given role:

.. code-block:: yaml

   ---
   dependencies:
     - role: ansible_plugins

This will make the ``ansible_plugins`` role a hard dependency of a given role,
which should ensure that the ``ansible_plugins`` role is always included, and
doesn't need to be included in all playbooks that use a given role.


Custom Ansible filter plugins
-----------------------------

The role contains a set of custom Ansible filter plugins which can be used in
Jinja templates:

``globmatch``
  This filter plugin can be used to filter strings or lists that match shell
  glob patterns.

``split``
  This filter plugin can be used to split strings, similarly to the
  ``.split()`` function in Python.


.. _ansible_plugins_config_filters:

Configuration filters
~~~~~~~~~~~~~~~~~~~~~

These filters are used to implement DebOps :ref:`universal_configuration`.
See the user-facing documentation for the behaviors they are meant to
facilitate.

``parse_kv_config``
  Parse a YAML list of dictionaries and output a sorted and expanded list of
  YAML dictionaries that contain a common set of dictionary keys. The filter
  supports dynamic order of the entries using weight model, and can be used to
  generate a configuration file which uses a key/value syntax with unique keys.

  The ``parse_kv_config`` filter accepts this argument:

  ``name``
    Optional, String. Defaults to ``name``.
    Sets the name of the field to be used as the unique key.


``parse_kv_items``
  This is a wrapper for the ``parse_kv_config`` filter which can be used in the
  looped Ansible tasks to manage multiple files with key/value syntax, or
  generate a configuration file with multiple key/value configuration
  structures.

  The ``parse_kv_items`` filter accepts the following arguments:

  ``name``
    Optional, String. Defaults to ``name``.
    Sets the name of the field to be used as the unique key.

  ``defaults``
    Optional, Dict. Keys are parameter names, values are default values to
    use when a parameter is not specified. Examples:

    .. code-block:: jinja

      {{ variable | parse_kv_items(defaults={'some_param': 'default_value'}) }}

  ``empty``
    Optional, Dict. Keys are fields which might be empty, values
    are other field names or lists of field names.

    The value of the first field with a value other than ``None`` will be used
    as the value of the specified field, if the specified field is empty.

    This behavior does not extend to fields in second-level lists, such as
    ``options`` or other defined ``merge_keys``.

    For example, running the filter with the following dict as ``empty``:

    .. code-block:: jinja

      {{ variable | parse_kv_items(
        empty={
          'some_param':  'other_param',
          'empty_param': ['param1', 'param2']
        })
      }}

    Will turn these input items:

    .. code-block:: yaml

      - name: foo
        other_param: bar

      - name: fizz
        param2: buzz

    Into ones looking like this (plus the extra fields described later on):

    .. code-block:: yaml

      - name: foo
        some_param: bar
        other_param: bar

      - name: fizz
        empty_param: buzz
        param2: buzz

  ``merge_keys``
    Optional. List of keys in the item that will be processed by the filter.
    If not specified, lists in the ``options`` field will be processed by default.


Output mappings
'''''''''''''''
These values get populated in the ``parse_kv_*`` output mappings:

- ``id``: The initial source order of the items in the input list ``* 10``.
- ``state`` defaults to ``present``
- ``weight``: The weight as defined in the source mapping. Defaults to ``0``.
- ``real_weight``: Calculated from adding ``weight`` and ``id``.
- ``section``: defaults to ``unknown``. Can be used by roles to split sections.
- ``separator``: defaults to ``False``.
  Can be used by roles to affect formatting.

Any other values in the mappings are preserved, so the ``parse_kv_*`` filters
can be used to weigh and merge arbitrary of mappings, as long as they have a
unique key field.

The filter plugins `source`__ contains tests you may find useful in better
understanding the ``parse_kv_*`` filters' behavior.

.. __: https://github.com/debops/debops/blob/master/ansible/roles/ansible_plugins/filter_plugins/debops_filter_plugins.py


Custom Ansible lookup plugins
-----------------------------

The role contains a set of custom Ansible lookup plugins which can be used in
Ansible roles:

``file_src``
  This lookup plugin allows "sideloading" files to copy into roles without the
  need to modify the roles themselves. It requires the ``debops`` Python module
  to be installed and uses configuration in :file:`.debops.cfg` to get a list
  of directories that are bases to look for custom files.

  If a file in specified subdirectory is found in one of the base directories,
  its path will be returned to Ansible to use as a file source. If no custom
  files are found, the lookup plugin returns the original path which
  corresponds to the file included in the role itself.

``lists``
  This lookup plugin implements the ``with_lists`` lookup. Similar to
  ``with_flattened`` lookup, the difference is the lists are not flattened all
  the way into a single list, therefore you can perform a "list of lists"
  tasks.

``task_src``
  This lookup plugin allows injection of custom Ansible tasks into roles without
  the need to modify the roles themselves. It requires the ``debops`` Python
  module to be installed and uses configuration in :file:`.debops.cfg` to get
  a list of directories that are bases to look for a list of Ansible tasks.

  If a file with list of tasks is found, they will be added to the Ansible
  playbook execution, usually as "pre" or "post" tasks at the beginning or end
  of a role. If no tasks are found, the plugin returns the path to
  a predefined, usually empty file with no tasks, that gets included by
  Ansible, avoiding the issue of missing task list. The roles that use this
  plugin need to be prepared for this usage beforehand.

``template_src``
  This lookup plugin allows "sideloading" Jinja templates into roles without
  the need to modify the roles themselves. It requires the ``debops`` Python
  module to be installed and uses configuration in :file:`.debops.cfg` to get
  a list of directories that are bases to look for templates.

  If a template file in specified subdirectory is found in one of the base
  directories, its path will be returned to Ansible to use as a template. If no
  custom templates are found, the lookup plugin returns the original path which
  corresponds to the template included in the role itself.
