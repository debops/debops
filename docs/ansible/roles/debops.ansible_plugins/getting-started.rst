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


Custom Ansible lookup plugins
-----------------------------

The role contains a set of custom Ansible lookup plugins which can be used in
Ansible roles:

``template_src``
  This lookup plugins allows "sideloading" Jinja templates into roles without
  the need to modify the roles themselves. It requires the ``debops`` Python
  module to be installed and uses configuration in :file:`.debops.cfg` to get
  a list of directories that are bases to look for templates.

  If a template file in specified subdirectory is found in one of the base
  directories, its path will be returned to Ansible to use as a template. If no
  custom templates are found, the lookup plugin returns the original path which
  corresponds to the template included in the role itself.
