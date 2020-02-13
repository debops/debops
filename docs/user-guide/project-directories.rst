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
   │   │── secret/
   │   │   ├── credentials/
   │   │   │   ├── host1/
   │   │   │   └── host2/
   │   │   ├── dhparam/
   │   │   │   └── params/
   │   │   │       ├── dh2048.pem
   │   │   │       └── dh3072.pem
   │   │   └── pki/
   │   │       ├── authorities/
   │   │       ├── ca-certificates/
   │   │       ├── lib/
   │   │       ├── realms/
   │   │       └── requests/
   │   └── global-vars.yml
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

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html#content-organization

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


.. _global_vars:

The :file:`ansible/global-vars.yml` file
----------------------------------------

This is an optional YAML file, not created by default. If the :command:`debops`
script detects this file, it will be provided to the
:command:`ansible-playbook` command using the ``--extra-vars`` parameter.
For Ansible to work correctly, this file has to contain at least one valid
variable, otherwise Ansible will return with an error.

The :file:`ansible/global-vars.yml` file `can contain global variables`__ which
will `override`__ any other variables in the inventory, playbooks or roles. In
DebOps, this file can be used to define variables which affect how playbooks
are processed by Ansible during initialization. For example, global variables
can be used to change the role used by the ``import_role`` Ansible module
without modifying the role/playbook code, which is only possible via the
``--extra-vars`` parameter since Ansible inventory variables are not available
at that stage.

.. warning:: Variables defined in the :file:`ansible/global-vars.yml` file
   should be treated as "global" for the entire environment managed by DebOps
   and shouldn't be scoped to a particular host or host group, otherwise
   unexpected things can happen.

If you don't use the :command:`debops` command to run DebOps playbooks, you
need to specify this file manually on the command line, for example:

.. code-block:: console

   ansible-playbook --extra-vars '@ansible/global-vars.yml' playbook.yml

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#passing-variables-on-the-command-line
.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#variable-precedence-where-should-i-put-a-variable


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


Overriding the ``site`` playbook
--------------------------------

:file:`debops/ansible/playbooks/site.yml` connects all debops roles.

By creating a playbook named :file:`ansible/playbooks/site.yml` inside your
project folder, you can override the debops version of :file:`site.yml`
and hook your role to the :command:`debops` command instead:

in :file:`ansible/playbooks/site.yml`:

.. code-block:: yaml

  ---
  - include: '{{ lookup("ENV", "HOME") + "/.local/share/debops/debops/ansible/playbooks/site.yml" }}'
  - include: your_role.yml


in :file:`ansible/playbooks/your_role.yml`:

.. code-block:: yaml

  ---
  - name: Manage the your specific setup
    hosts: [ 'debops_all_hosts' ]
    roles:
      - role: ansible.your_role
        tags: [ 'role::your_role' ]


.. note::

  Note that the path to :file:`debops/ansible/playbooks/site.yml`
  can vary per OS and installation method.
  You can either provide the path to the playbook,
  or create a symlink to the correct destination in your project folder.

You can override any of the other DebOps playbooks in a similar fashion.
