.. _project_directory:

Project directories
===================

DebOps uses a concept of "project directories" to store the data required to
manage an IT infrastructure. Each project directory is responsible for a single
environment, which usually means a single Ansible inventory which may contain
multiple hosts divided by groups of hosts.

Directory layout
----------------

Project directories are stored on the Ansible Controller host. They can be
created using the :command:`debops-init` command:

.. code-block:: console

   debops-init ~/src/projects/project1

The above command will create a base set of subdirectories in specified
directory and generate an initial Ansible inventory :file:`hosts` file:

.. code-block:: none

   ~/src/projects/project1/
   ├── ansible/
   │   ├── inventory/
   │   │   ├── group_vars/
   │   │   │   └── all/
   │   │   ├── host_vars/
   │   │   └── hosts
   │   ├── playbooks/
   │   └── roles/
   ├── .debops.cfg
   └── .gitignore

This is an example of a project directory after it was used to configure a few
hosts using DebOps roles and playbooks (some of the directory contents are
trimmed to make the result easier to read):

.. code-block:: none

   ~/src/projects/project1/
   ├── ansible/
   │   ├── inventory/
   │   │   ├── group_vars/
   │   │   │   ├── all/
   │   │   │   │   ├── apt.yml
   │   │   │   │   └── users.yml
   │   │   │   ├── appservers/
   │   │   │   │   ├── php.yml
   │   │   │   │   └── ruby.yml
   │   │   │   └── webservers/
   │   │   │       └── nginx.yml
   │   │   ├── host_vars/
   │   │   │   ├── host1/
   │   │   │   │   └── sshd.yml
   │   │   │   └── host2/
   │   │   │       └── nginx.yml
   │   │   └── hosts
   │   ├── playbooks/
   │   │   └── deployment.yml
   │   ├── resources/
   │   │   ├── res-dir1/
   │   │   │   └── res-file1.zip
   │   │   └── res-dir2/
   │   │       └── res-file2.jpg
   │   ├── roles/
   │   │   ├── service1/
   │   │   └── service2/
   │   └── secret/
   │       ├── credentials/
   │       │   ├── host1/
   │       │   └── host2/
   │       ├── dhparam/
   │       │   └── params/
   │       │       ├── dh2048.pem
   │       │       └── dh3072.pem
   │       └── pki/
   │           ├── authorities/
   │           ├── ca-certificates/
   │           ├── lib/
   │           ├── realms/
   │           └── requests/
   ├── debops/
   ├── .git/
   ├── playbooks/
   │   └── custom_play.yml
   ├── roles/
   │   ├── custom_role1/
   │   └── custom_role2/
   ├── ansible.cfg
   ├── .debops.cfg
   └── .gitignore

You can compare this directory structure with `Ansible Best Practices directory
organization`__ documentation to see where the solutions proposed by Ansible
and those implemented in DebOps overlap.

.. __: https://docs.ansible.com/ansible/latest/playbooks_best_practices.html#content-organization

Usually the :command:`debops` or :command:`ansible` commands are executed from
the root of the project directory. At the moment there are no safeguards
against running multiple :command:`debops` commands at the same time; it's
advisable not to do it due to possible deadlocks and issues with concurrent
execution of Ansible commands on the same resources located on the remote
hosts.

As you can see, the project directory can be managed using :command:`git` to
keep the history of the changes over time and share a given environment among
team members. It's also possible to create a "public" project directory and
share it on hosting platforms like GitHub - the `DebOps for WordPress`__
project is essentially this.

.. __: https://github.com/carlalexander/debops-wordpress/


The :file:`ansible/inventory/` directory
----------------------------------------

This is the directory where Ansible will look for its inventory. In the example
above, it's a static inventory based on an INI file format, however if you wish
you can switch it to a dynamic inventory generated from a database; just
replace the :file:`ansible/inventory/hosts` file with a script.

The inventory variables can be put either in a single file, or multiple files,
which might be more convenient if you want to share the same variables across
project directories using symlinks. Just remember that you cannot mix
directories and files on the same level of the inventory directory structure.


Role and playbook directories
-----------------------------

There are two sets of directories that can hold Ansible playbooks and roles in
the project directory, :file:`playbooks/` and :file:`roles/` as well as
:file:`ansible/playbooks/` and :file:`ansible/roles/`. They are functionally
equivalent and you are free to use them as you see fit; common usage could be
using the subdirectories in the :file:`ansible/` directory for playbooks and
roles that are in production use in a given environment, and reserve the
"plain" subdirectories for temporary and/or test code.


The :file:`ansible/resources/` directory
----------------------------------------

This directory can be used to store various files which can be accessed by the
:ref:`debops.resources` Ansible role to copy them over to the remote hosts.


The :file:`ansible/secret/` directory
-------------------------------------

This directory is maintained by the :ref:`debops.secret` Ansible role. You can
find there plaintext passwords, randomly generated by different roles, as well
as PKI configuration and some other data - the directory is sometimes used to
distribute public keys or other information between hosts via Ansible
Controller.


The :file:`debops/` directory
-----------------------------

This directory can contain a local copy of the DebOps monorepo, or a symlink to
it, or even a :command:`git` submodule, scoped to a given environment. This can
be useful to have a separate development environment where you work on the main
DebOps roles, separate from the official DebOps monorepo used in production
environments stored in other project directories.


The :file:`ansible.cfg` file
----------------------------

This is a configuration file read by the :command:`ansible` and
:command:`ansible-playbook` commands. It's automatically generated and updated
by the :command:`debops` command to include the DebOps monorepo in various
configuration variables, so Ansible can correctly find playbooks and roles
provided by DebOps. You shouldn't modify it manually, it will be overwritten on
the next execution.


The :file:`.debops.cfg` file
----------------------------

The :command:`debops` command is looking for this file for current directory to
see if it's a project directory; if it's not found the execution is aborted to
not cause issues in the filesystem.

This file contains configuration for some of the custom DebOps lookup plugins,
as well as configuration which should be added to the automatically generated
:file:`ansible.cfg` configuration file.
