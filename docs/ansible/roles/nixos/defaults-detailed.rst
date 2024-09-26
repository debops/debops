.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.nixos`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _nixos__ref_repositories:

nixos__repositories
-------------------

These lists can be used to clone or update remote :command:`git` repositories.
The :command:`git` repositories will be cloned as the UNIX ``root`` account by
default. The NixOS system will be rebuilt automatically on changes in
repositories.

Examples
~~~~~~~~

Clone an example NixOS configuration repository and ensure that the
:file:`/etc/nixos/` directory is replaced correctly. Files existing in the
directory before cloning will be archived and restored; old files will not
replace new ones committed in the repository.

.. code-block:: yaml

   nixos__repositories:

     - repo: 'https://github.com/prikhi/nixos-config'
       version: 'master'

And the required command to do this the first time:

.. code-block:: console

   debops run nixos -e 'nixos__git_resync=true'

After first repository clone, additional variable does not need to be
specified. If the repositories are not cloned into the :file:`/etc/nixos/`
directory directly, the variable doesn't have to be used.

Syntax
~~~~~~

You can use all parameters of the :command:`git` Ansible module to manage the
repositories, with some exceptions. The role recognizes these additional
parameters:

``repo``
  Required. The URL of the :command:`git` repository to clone.

``version``
  Required. Specify the tag or branch, which should be checked out.

``dest``
  Optional. Path where the specified repository should be cloned to.

  If not specified, the default destination will be :file:`/etc/nixos/`, which
  requires special treatment before being usable as a :command:`git`
  repository. Check :ref:`nixos__ref_in_git` for more details.

``force``
  Optional, boolean. If set to ``True`` and the destination repository has
  non-committed modifications, they will be removed and overwritten.

``_update``
  Optional, boolean. This is a replacement of the ``update`` :command:`git` module
  parameter, due to the string being a reserved word in Python. You can use
  this to enable or disable repository update.

``owner``
  Optional. If specified, the role will use the Ansible ``become``
  functionality to switch to a specified UNIX user account before cloning the
  repository. The account must exist on the host before it can be used. If not
  specified, the role will use the ``root`` account.

  The specified UNIX account needs to have access to the destination directory.
  The parent directories are created automatically, as long as the access
  permissions allow.


.. _nixos__ref_configuration:

nixos__configuration
--------------------

These lists can be used to generate and manage NixOS configuration files,
located in the :file:`/etc/nixos/` directory. Each configuration entry defines
a single file. Entries are managed using the :ref:`universal_configuration`
system. Any changes in configuration trigger a rebuild of the NixOS system.

Examples
~~~~~~~~

Create an example configuration file in a subdirectory (a silly example):

.. code-block:: yaml

   nixos__configuration:

     - name: 'flakes/system.nix'
       raw: |
         {
           description = "Custom system configuration";

           inputs = {
             nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05"
           };

           outputs = { nixpkgs, ... }: {
             nixosConfigurations.nixos = nixpkgs.lib.nixosSystem {
               system = "x86_64-linux";
               modules = [ ../configuration.nix ];
             };
           };
         }
       state: 'present'

An example definition of the :file:`/etc/nixos/configuration.nix` configuration
file can be found in the :envvar:`nixos__default_configuration` variable.

Syntax
~~~~~~

Configuration entries are defined as YAML dictionaries in a list with specific
parameters:

``name``
  Required. Name of the configuration file to manage in the :file:`/etc/nixos/`
  directory. The name can contain subdirectories separated by slashes. Each
  configuration entry requires an unique ``name`` parameter, multiple entries
  with the same ``name`` will be merged at runtime and will override their
  parameters in order of appearance.

``raw``
  Required. String or YAML text block with contents of the configuration file.

``comment``
  Optional. String or YAML text block with a comment added at the top of the
  generated configuration file.

``state``
  Optional. If not specified or ``present``, a given configuration file will be
  generated in the :file:`/etc/nixos/` directory. If ``absent``, a given
  configuration file will be removed from the host (subdirectories are not
  removed). If ``init``, a given configuration entry will be prepared, but it
  will not be enabled by default; subsequent configuration entry with the same
  ``name`` and ``present`` state can enable a prepared entry. If ``ignore``,
  a given configuration entry will be ignored at runtime.

``mode``
  Optional. String with the file mode to set during generation. If not
  specified, ``0644`` will be used by default.


.. _nixos__ref_templates:

nixos__templates
----------------

The :ref:`debops.nixos` role supports dynamic generation of directories,
templated files and symlinks using the `with_filetree`__ Ansible lookup plugin.

.. __: https://docs.ansible.com/ansible/2.5/plugins/lookup/filetree.html

The file, directory and symlink management is limited - the managed files
will be owned by ``root`` UNIX account and will be placed in the ``root`` UNIX
group, however the specific file mode will be preserved; for example if you
create a file with ``0600`` permissions, the same permissions will be set by
the role on the remote host.

.. warning::

   The task ensures that each directory in the path exists, including
   permissions. You have to set specific permissions for certain directories
   like :file:`/root` (``0700``) or :file:`/tmp` (``1777``)  in order to not
   modify them in unexpected manner.

For this functionality to work, the role expects a specific directory structure
located in the :file:`ansible/views/<view>/nixos/` directory (or wherever the
:envvar:`nixos__src` variable points to):

.. code-block:: none

   ansible/views/<view>/nixos/
   └── templates/
       ├── by-group/
       │   ├── all/
       │   │   └── etc/
       │   │       └── nixos/
       │   │           └── configuration.nix
       │   ├── group-name1/
       │   │   └── etc/
       │   │       └── nixos/
       │   │           └── configuration.nix
       │   └── group-name2/
       │       └── etc/
       │           └── nixos/
       │               └── configuration.nix
       └── by-host/
           ├── hostname1/
           │    └── etc/
           │        └── nixos/
           │            └── configuration.nix
           └── hostname2/
               └── etc/
                   └── nixos/
                       └── configuration.nix

The ``with_filetree`` Ansible lookup plugin will look for configuration files
to manage in specific hostname directory, then of all the groups the current
host is in (based on the content of the variable `group_names`), then in the
:file:`by-group/all/` directory. The configuration file found first in this
order wins and no further checks are performed; this means that you can put
a file in the :file:`by-group/all/` directory and then override it using
a host-specific directory. The groups directories are read in the order
dictated by Ansible during inventory parsing.

See `Ansible - Playbooks Variables`__ to learn about the ``group_names``
variable, and `Ansible - Working with Inventory`__ for more information on how
to use ``ansible_group_priority`` to change the merge order for groups of the
same level (after the parent/child order is resolved).

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#accessing-information-about-other-hosts-with-magic-variables
.. __: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#how-variables-are-merged

Each directory structure starts at the root of the filesystem (:file:`/`), so
to create a file in a subdirectory you need to recreate the entire path. For
example, to create the :file:`/var/lib/application/custom.txt` file, it needs
to be placed in:

.. code-block:: none

   ansible/views/<view>/nixos/templates/by-group/all/var/lib/application/custom.txt

In the templates, you can reference variables from the Ansible facts (including
local facts managed by other roles) and Ansible inventory. Referencing
variables from other roles might work only if these roles are included in the
playbook, however that is not idempotent and should be avoided.
