.. Copyright (C) 2021-2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops project init`
------------------------------

This command can be used to initialize a new project directory, specified as
the main argument. The script will check if a :file:`.debops.cfg` file exists
in a given directory; if not, it will be created along with a basic directory
structure.

This command executes :ref:`hook scripts <debops_hooks>` (``pre-init`` and
``post-init``) before and after project initialization.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-t <legacy|modern>``, ``--type <legacy|modern>``
  Select the type of the project directory:

  - ``legacy``: simple directory layout with a single Ansible inventory
    (default)

  - ``modern``: more complicated directory layout with multiple Ansible
    inventories separated into "infrastructure views"

``-V <view>``, ``--default-view <view>``
  Specify the name of the "infrastructure view" used by default. If not
  specified, "system" will be created automatically. You can use slashes
  (``/``) to create hierarchical views, but nesting a view inside of another
  view is not allowed.

``--git``
  Initialize a :command:`git` repository in the project directory (default)

``--no-git``
  Do not initialize a :command:`git` repository by default

``--requirements``
  After the project directory is initialized, install Ansible Collections
  specified in the :file:`ansible/collections/requirements.yml` file using the
  :command:`ansible-galaxy` command. This will be done by default in new DebOps
  projects.

``--no-requirements``
  Don't install Ansible Collections after the project directory is initialized.

``--venv``
  Enable an encapsulated Python virtual environment in the new project
  directory (modern projects only). The environment lives in the
  :file:`.debops/venv/` subdirectory and contains its own Ansible installation
  along with the Python dependencies required by the DebOps roles, independent
  of the system packages. By default, in a new project directory Python
  packages and Ansible Collections will be installed automatically; this can be
  turned off using ``--no-requirements`` option to allow for customization of
  the environment, which can be installed later with the :command:`debops
  project venv install` command. See :command:`debops project venv` for more
  details.

``--no-venv``
  Don't enable a Python virtual environment in the new project directory
  (default).

``--encrypt <encfs|git-crypt>``
  Prepare the project directory to host encrypted :file:`ansible/secret/`
  subdirectory, used to store passwords, encryption keys and other confidential
  information. See the :ref:`debops.secret` Ansible role for more details.

  You need to specify either ``encfs`` or ``git-crypt`` to select the encryption
  method (``git-crypt`` requires an initialized ``git`` repository). If
  encryption is enabled, you need to specify the list of GPG recipients as well,
  using the ``--keys`` option.

``--keys <recipient>[,recipient]``
  A list of GPG recipients (e-mail addresses or key IDs) which will be allowed
  to unlock the :file:`ansible/secret/` directory encrypted with EncFS or
  git-crypt. Separate multiple list entries by commas.

``--template <spec>``
  Create Ansible inventory structure in the selected or default view, described
  by a :ref:`inventory specification <inventory_specification>`. This
  option can be specified multiple times; the specification sources are merged
  before they are applied.

  The value is resolved in order: ``-`` reads the document from standard
  input, a name matching a template shipped with DebOps (``hosts`` for remote
  hosts, ``local`` for the local machine, ``clear`` to reset the inventory,
  ``sshkeys`` to grant the SSH agent's public keys access) loads that
  template, and anything else is read as a file. A template name wins over a
  file of the same name; use ``./hosts`` to load such a file.

``-n``, ``--dry-run``
  Describe the changes which the specification would make, without writing
  them. The project directory itself is still created or refreshed.

``--force``
  Overwrite, clear or remove inventory paths which already exist. Inventory
  paths listed in a specification's ``keep`` key are not affected by this
  option. See :ref:`inventory_specification` for the default behavior.

``--allow-io``
  Allow a version 3 specification to run commands with ``pipe()`` and read
  files with ``include()``. Without this option such a document is refused.

``--graph``
  Display the Ansible inventory graph after the specification has been
  applied, to confirm that Ansible reads the files the way you expect.
  Mutually exclusive with ``--list`` and ``--host``.

``--list``
  Display the Ansible inventory as JSON after the specification has been
  applied, like :command:`ansible-inventory --list`. Mutually exclusive with
  ``--graph`` and ``--host``.

``--host <hostname>``
  Display the variables Ansible resolves for the given host after the
  specification has been applied, like :command:`ansible-inventory --host`.
  Mutually exclusive with ``--graph`` and ``--list``.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the DebOps project directory to initialize. If not specified, DebOps
  will try to use the current directory to create a new project directory. The
  script will check if the current directory is a home directory and will stop
  operation in this case.

Examples
~~~~~~~~

Create a basic DebOps project directory:

.. code-block:: shell

   debops project init ~/src/projects/myproject

Create a project directory with multiple infrastructure views:

.. code-block:: shell

   debops project init --type modern ~/src/projects/myproject

Create a project directory with EncFS encryption for secrets:

.. code-block:: shell

   debops project init --encrypt encfs \
                       --keys admin@example.org,otheradmin@example.org \
                       ~/src/projects/example.org

Create a project directory with an inventory read from standard input:

.. code-block:: shell

   debops project init --template - ~/src/projects/example.org <inventory.yml


:command:`debops project mkview`
--------------------------------

This command can be used in an existing project directory to create a new
"infrastructure view", which contains:

- separate :file:`ansible.cfg` configuration file

- separate Ansible inventory

- separate :file:`secret/` directory for the :ref:`debops.secret` role

- separate :file:`resources/` directory for the :ref:`debops.resources` role

- its own set of Ansible playbooks and roles

Each view has its own configuration entry in the DebOps configuration tree.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--project-dir <project_dir>``
  Path to the project directory to work on. If it's not specified, the script
  will use the current directory.

``--encrypt <encfs|git-crypt>``
  Prepare the new infrastructure view to host encrypted :file:`<view>/secret/`
  subdirectory, used to store passwords, encryption keys and other confidential
  information. See the :ref:`debops.secret` Ansible role for more details.

  You need to specify either ``encfs`` or ``git-crypt`` to select the encryption
  method. If encryption is enabled, you need to specify the list of GPG
  recipients as well, using the ``--keys`` option.

``--keys <recipient>[,recipient]``
  A list of GPG recipients (e-mail addresses or key IDs) which will be allowed
  to unlock the :file:`<view>/secret/` directory encrypted with EncFS or
  git-crypt. Separate multiple list entries by commas.

``--template <spec>``
  Create inventory files in the new view, described by a :ref:`inventory file
  specification <inventory_specification>`. The value is resolved in
  order: ``-`` reads the document from standard input, a name matching a
  template shipped with DebOps (``hosts`` for remote hosts, ``local`` for the
  local machine, ``clear`` to reset the inventory, ``sshkeys`` to grant the
  SSH agent's public keys access) loads that template, and anything else is
  read as a file. This option can be given more than once; the specification
  sources are merged before they are applied.

``-n``, ``--dry-run``
  Describe the changes which the specification would make, without writing
  them. The project directory itself is still created or refreshed.

``--force``
  Overwrite, clear or remove inventory paths which already exist. Inventory
  paths listed in a specification's ``keep`` key are not affected by this
  option.

``--allow-io``
  Allow a version 3 specification to run commands with ``pipe()`` and read
  files with ``include()``. Without this option such a document is refused.

``--graph``
  Display the Ansible inventory graph after the specification has been
  applied. Mutually exclusive with ``--list`` and ``--host``.

``--list``
  Display the Ansible inventory as JSON after the specification has been
  applied. Mutually exclusive with ``--graph`` and ``--host``.

``--host <hostname>``
  Display the variables Ansible resolves for the given host after the
  specification has been applied. Mutually exclusive with ``--graph`` and
  ``--list``.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<new_view>``
  Name of the view to create. It will be used in the file system as well as in
  the configuration tree. You can use slashes (``/``) to create hierarchical
  views, but nesting a view inside of another view is not allowed.

Examples
~~~~~~~~

Create a new infrastructure view in the DebOps project directory:

.. code-block:: shell

   debops project mkview deployment

Create a new infrastructure view with encrypted secrets:

.. code-block:: shell

   debops project mkview --encrypt encfs \
                         --keys admin@example.org,otheradmin@example.org \
                         deployment


:command:`debops project commit`
--------------------------------

This command can be used to commit current contents of the project directory
into the :command:`git` repository. Any modifications to the existing files as
well as any untracked files will be committed automatically. The commit message
is taken from the DebOps configuration; users can use :command:`git commit
--amend` command to edit the commit message afterwards.

This command executes :ref:`hook scripts <debops_hooks>` (``pre-commit`` and
``post-commit``) before and after the git commit.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the project directory to refresh.


:command:`debops project refresh`
---------------------------------

This command can be used to "refresh" a given DebOps project directory. By
default DebOps does not modify an existing :file:`ansible.cfg` configuration
file. This allows the user to test new configuration if needed. When the
:command:`debops project refresh` command is called, DebOps will generate a new
:file:`ansible.cfg` configuration file based on the contents of its own
internal configuration. The script will also ensure that the basic directory
structure of a project exists.

This command executes :ref:`hook scripts <debops_hooks>` (``pre-refresh`` and
``post-refresh``) before and after the refresh.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-V <view>``, ``--view <view>``
  Specify the name of the "infrastructure view" to refresh. If not specified,
  the default view will be refreshed. Using this option overrides the
  automatic view detection performed by DebOps based on the current working
  directory.

``--template <spec>``
  Create inventory files in the selected view, described by a :ref:`inventory
  file specification <inventory_specification>`. Without this option
  the view is refreshed with DebOps' internal defaults only. The value is
  resolved in order: ``-`` reads the document from standard input, a name
  matching a template shipped with DebOps (``hosts`` for remote hosts,
  ``local`` for the local machine, ``clear`` to reset the inventory,
  ``sshkeys`` to grant the SSH agent's public keys access) loads that
  template, and anything else is read as a file. This option can be given
  more than once; the specification sources are merged before they are
  applied.

``-n``, ``--dry-run``
  Describe the changes which the specification would make, without writing
  them. The project directory itself is still refreshed.

``--force``
  Overwrite, clear or remove inventory paths which already exist. This is
  usually what you want when reapplying a specification to an existing project,
  because otherwise paths you have already edited are kept. Inventory paths
  listed in a specification's ``keep`` key are not affected by this option.

``--allow-io``
  Allow a version 3 specification to run commands with ``pipe()`` and read
  files with ``include()``. Without this option such a document is refused.

``--graph``
  Display the Ansible inventory graph after the specification has been
  applied. Mutually exclusive with ``--list`` and ``--host``.

``--list``
  Display the Ansible inventory as JSON after the specification has been
  applied. Mutually exclusive with ``--graph`` and ``--host``.

``--host <hostname>``
  Display the variables Ansible resolves for the given host after the
  specification has been applied. Mutually exclusive with ``--graph`` and
  ``--list``.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the DebOps project directory to refresh.

Examples
~~~~~~~~

Refresh the project directory using DebOps' internal defaults:

.. code-block:: shell

   debops project refresh ~/src/projects/myproject

Apply an inventory file specification to the default view and check the
result without writing anything:

.. code-block:: shell

   debops project refresh --dry-run --graph \
                          --template inventory.yml \
                          ~/src/projects/myproject


:command:`debops project unlock`
--------------------------------

When the project directory contains an encrypted :file:`ansible/secret/`
directory, this command can be used to unlock it and provide access to
encrypted data. This only works for project directories that have been
initialized with EncFS or git-crypt support (or that support has been configured
manually).

Keep in mind that after unlocking the directory manually, DebOps will not lock it
on subsequent Ansible runs. In such case you should use the :command:`debops
project lock` command to secure the secrets.

When ``git-crypt`` is used to encrypt secrets, unlocking them will fail if the
``git`` working directory contains uncommitted changes. This is expected
behavior. Easiest way to mitigate this is to unlock the project before making
any changes.

This command executes :ref:`hook scripts <debops_hooks>` (``pre-unlock`` and
``post-unlock``) before and after unlocking the secrets.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to unlock. If not specified,
  the default view will be used automatically. Using this option overrides the
  automatic view detection performed by DebOps based on the current working
  directory.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the project directory to unlock.


:command:`debops project lock`
------------------------------

This command can be used to lock and secure the :file:`ansible/secret/`
directory after it has been unlocked using the :command:`debops project unlock`
command. This only works in project directories that have been configured with
either EncFS or git-crypt encryption during initialization.

When ``git-crypt`` is used to encrypt secrets, locking them will fail if the
``git`` working directory contains uncommitted changes. This is expected
behavior. Easiest way to mitigate this is to commit any changes before locking
the project directory.

This command executes :ref:`hook scripts <debops_hooks>` (``pre-lock`` and
``post-lock``) before and after locking the secrets.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-V <view>, --view <view>``
  Specify the name of the "infrastructure view" to lock. If not specified, the
  default view will be used automatically. Using this option overrides the
  automatic view detection performed by DebOps based on the current working
  directory.

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the project directory to lock.


:command:`debops project venv`
------------------------------

This command manages the Python virtual environment encapsulated in
a "modern" DebOps project directory, enabled either at creation time with
the :command:`debops project init --venv` command or later with the
``enable`` action. The environment lives in the :file:`.debops/venv/`
subdirectory and contains its own Ansible installation along with the Python
dependencies required by the DebOps roles, independent of the system
packages. The installed package versions are recorded in the
:file:`.debops/requirements.txt` file, and the versions of the installed
Ansible Collections in the :file:`ansible/collections/requirements.lock.yml`
file; both are meant to be committed to version control. The environment
itself is not, and can be recreated on demand. When git auto-commit is
enabled, changes to the requirements files are committed automatically.

While the environment is enabled, its :file:`bin/` directory is prepended to
the ``PATH`` environment variable at runtime, so :command:`debops env` and
the other subcommands use the binaries from the environment; the ``ansible``
binaries used by the :command:`debops` subcommands are likewise resolved
into the environment at runtime. An explicit ``PATH`` entry in the
:file:`.debops/environment` file overrides the runtime ``PATH``.

The ``project.venv.path`` configuration option can be an absolute path
outside of the project directory, which allows multiple projects to share
one environment. Note that in that case the
:file:`.debops/requirements.txt` file of each project mirrors the full
contents of the shared environment, and upgrading the packages in one
project affects the other projects as well.

Available actions:

``enable``
  Activate the Python virtual environment in an existing "modern" project
  directory. This writes the same configuration which a project created with
  :command:`debops project init --venv` configures in a new project directory.
  Existing configuration files will be modified to encapsulate the environment
  (for example, ``collections_path`` parameter in Ansible configuration will be
  rewritten to use only the project directory :file:`ansible/collections/`
  path).

  After enabling the environment, the :command:`debops project venv install`
  command can be used to install the specified Python packages and Ansbile
  Collections.

``install``
  Create the virtual environment if it does not exist yet and install the
  Python packages from the :file:`.debops/requirements.txt` file (or the DebOps
  seed if the file is missing). Ansible Collections are installed from the
  :file:`ansible/collections/requirements.lock.yml` file if it exists (which
  reproduces the locked versions), followed by the
  :file:`ansible/collections/requirements.yml` file, which applies new or
  changed entries on top. The requirements files are rewritten afterwards with
  the pinned versions of everything installed. New packages can be added to the
  requirements file by hand and installed by running this action again.

  Some of the Python packages in the DebOps seed, for example
  ``python-ldap``, need external, system-level build dependencies such as
  a C compiler and development files. DebOps checks for their presence on
  the Ansible Controller; where they are missing, the affected packages are
  commented out in the requirements file, together with the command needed
  to install the dependencies on the detected platform (APT, DNF, Pacman,
  APK, Zypper or Homebrew). After installing the dependencies, uncomment the
  package and run this action again to add it to the environment.

``upgrade``
  Upgrade the Python packages listed in the DebOps seed which are present in
  the requirements file, along with their dependencies, and force-upgrade
  the Ansible Collections from the
  :file:`ansible/collections/requirements.yml` file. Packages added to the
  requirements file by the user stay at their pinned versions. The
  requirements files are rewritten afterwards with the new pinned versions.

``recreate``
  Destroy the virtual environment and install it from scratch, using the
  current contents of the requirements files. This action can be used during
  downgrades of Python packages or Ansible Collections to help with dependency
  resolution.

``freeze``
  Rewrite the requirements files with the pinned versions of the Python
  packages and Ansible Collections currently installed in the project. The
  versions of the Ansible Collections listed in the
  :file:`ansible/collections/requirements.yml` file are recorded in the
  :file:`ansible/collections/requirements.lock.yml` file alongside it, which
  is meant to be committed to version control and can be used to reinstall
  the recorded state with :command:`ansible-galaxy collection install -r`.
  Collections with a source other than Ansible Galaxy (for example a git
  repository) are preserved as written in the requirements file, with the
  installed version recorded in a comment when it can be determined.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``--python``
  Manage only the Python packages and the virtual environment. Mutually
  exclusive with ``--collections`` and ``--all``.

``--collections``
  Manage only the Ansible Collections. Mutually exclusive with ``--python``
  and ``--all``.

``--all``
  Manage both the Python packages and the Ansible Collections (default).

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the project directory to manage.

Examples
~~~~~~~~

Activate the Python virtual environment in an existing project directory:

.. code-block:: console

   debops project venv enable

Create the virtual environment and install all requirements:

.. code-block:: console

   debops project venv install

Upgrade Ansible and the other seed packages to their latest versions:

.. code-block:: console

   debops project venv upgrade

Install only the Ansible Collections, leaving the Python packages alone:

.. code-block:: console

   debops project venv install --collections
