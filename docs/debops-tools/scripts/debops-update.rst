.. _cmd_debops-update:

The :command:`debops-update` command
====================================

The :command:`debops-update` script clones the DebOps monorepo from GitHub, or
updates an existing DebOps repository. If a custom directory is not specified
as the first argument, the script will operate on the

.. code-block:: none

   ~/.local/share/debops/debops/

directory. By default the ``master`` branch is cloned and checked out;
afterwards the user can use the :command:`git checkout` command to switch to
a different branch.

If a relative or absolute directory is specified as an argument, the
:command:`debops-update` script will clone the DebOps monorepo to the
:file:`debops/` subdirectory of that directory. This can be used to create
a local copy of the repository in a "project directory" which contains the
Ansible inventory and other files:

.. code-block:: none

   debops-init ~/src/projects/example.org
   cd ~/src/projects/example.org
   debops-update ./

The :command:`debops` script knows how to use both the contents of the
:file:`debops/` subdirectory in a project directory, or the central location,
and will switch between them automatically.

The script can also be executed with the ``--dry-run`` parameter. In that case,
no changes will be made to the existing repository; instead the script will
show the changes between current :command:`git` checkout and the remote
repository. This can be used to review any changes before applying them.
