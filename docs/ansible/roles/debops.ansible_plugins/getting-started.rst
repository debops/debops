Getting started
===============

.. contents::
   :local:
   :depth: 1

Usage as a role dependency
--------------------------

To use the custom Ansible plugins from this role in your own Ansible roles, you
should include the ``debops.ansible_plugins`` role as a dependency, in
:file:`meta/main.yml` file of a given role:

.. code-block:: yaml

   ---
   dependencies:
     - role: debops.ansible_plugins

This will make the ``debops.ansible_plugins`` role a hard dependency of a given
role, which should ensure that the ``debops.ansible_plugins`` role is always
included, and doesn't need to be included in all playbooks that use a given
role.


Custom Ansible filter plugins
-----------------------------

The role contains a set of custom Ansible filter plugins which can be used in
Jinja templates:

``globmatch``
  This filter plugin can be used to filter strings or lists that match shell
  glob patterns.

``parse_kv_config``
  Parse a YAML list of dictionaries and output a sorted and expanded list of
  YAML dictionaries that contain a common set of dictionary keys. The filter
  supports dynamic order of the entries using weight model, and can be used to
  generate a configuration file which uses a key/value syntax with unique keys.

``parse_kv_items``
  This is a wrapper for the ``parse_kv_config`` filter which can be used in the
  looped Ansible tasks to manage multiple files with key/value syntax, or
  generate a configuration file with multiple key/value configuration
  structures.

``split``
  This filter plugin can be used to split strings, similarly to the
  ``.split()`` function in Python.

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
