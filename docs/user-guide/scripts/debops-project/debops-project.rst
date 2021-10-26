.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
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

``--git``
  Initialize a :command:`git` repository in the project directory (planned)

``--no-git``
  Do not initialize a :command:`git` repository, if it's created by default
  (planned)

``--encrypt <encfs|git-crypt>``
  Prepare the project directory to host encrypted :file:`ansible/secret/`
  subdirectory, used to store passwords, encryption keys and other confidential
  information. See the :ref:`debops.secret` Ansible role for more details.

  You need to specify either ``encfs`` or ``git-crypt`` (planned) to select the
  encryption method. If encryption is enabled, you need to specify the list of
  GPG recipients as well, using the ``--keys`` option.

``--keys <recipient>[,recipient]``
  A list of GPG recipients (e-mail addresses or key IDs) which will be allowed
  to unlock the :file:`ansible/secret/` directory encrypted with EncFS or
  git-crypt. Separate multiple list entries by commas.

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

Create a project directory with EncFS encryption for secrets:

.. code-block:: shell

   debops project init --encrypt encfs \
                       --keys admin@example.org,otheradmin@example.org \
                       ~/src/projects/example.org


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

``<project_dir>``
  Path to the project directory to refresh.


:command:`debops project unlock`
--------------------------------

When the project directory contains an encrypted :file:`ansible/secret/`
directory, this command can be used to unlock it and provide access to
encrypted data. This only works for project directories that have been
initialized with EncFS or git-crypt support (or that suppor has been configured
manually).

Keep in mind that after unlocking the directory manually, DebOps will not lock it
on subsequent Ansible runs. In such case you should use the :command:`debops
project lock` command to secure the secrets.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``<project_dir>``
  Path to the project directory to unlock.


:command:`debops project lock`
------------------------------

This command can be used to lock and secure the :file:`ansible/secret/`
directory after it has been unlocked using the :command:`debops project unlock`
command. This only works in project directories that have been configured with
either EncFS or git-crypt encryption during initialization.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``<project_dir>``
  Path to the project directory to lock.


:command:`debops project status`
--------------------------------

This command displays various information about a given project directory known
to DebOps, for example the type of the project directory, state of encrypted
:file:`ansible/secret/` directory, and so on.

Options
~~~~~~~

``-h, --help``
  Display the help and usage information

``<project_dir>``
  Path to the project directory to inspect.
