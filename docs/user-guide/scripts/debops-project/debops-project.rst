.. Copyright (C) 2021-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

:command:`debops project init`
------------------------------

This command can be used to initialize a new project directory, specified as
the main argument. The script will check if a :file:`.debops.cfg` file exists
in a given directory; if not, it will be created along with a basic directory
structure.

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

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``-v, --verbose``
  Increase output verbosity. More letters means higher verbosity.

``<project_dir>``
  Path to the project directory to refresh.


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
