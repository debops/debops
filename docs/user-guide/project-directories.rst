.. Copyright (C) 2015-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Tasos Alvas <tasos.alvas@qwertyuiopia.com>
.. Copyright (C) 2015-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _project_directory:

Project directories
===================

DebOps uses a concept of "project directories" to store the data required to
manage an IT infrastructure. Project directories are kept on the Ansible
Controller hosts from where Ansible commands are executed. They are designed to
be tracked using :command:`git` version control and have support for encrypted
secret storage using `EncFS`__ or `git-crypt`__ projects.

.. __: https://vgough.github.io/encfs/
.. __: https://www.agwa.name/projects/git-crypt/

There are currently two versions of project directories supported by DebOps
- "legacy" and "modern".


The "legacy" directory layout
-----------------------------

This was the first directory layout designed for DebOps. This directory layout
is focused on a single Ansible inventory. To create it, you can run the
command:

.. code-block:: console

   debops project init --type legacy ~/src/projects/project1

The above command will create a base set of subdirectories in specified
directory and generate an initial Ansible inventory :file:`hosts` file:

.. code-block:: none

   ~/src/projects/project1/
   ├── ansible/
   │   ├── collections/
   │   │   ├── ansible_collections/
   │   │   └── requirements.yml
   │   ├── inventory/
   │   │   ├── group_vars/
   │   │   │   └── all/
   │   │   │       └── keyring.yml
   │   │   ├── hosts
   │   │   └── host_vars/
   │   ├── keyring/
   │   ├── overrides/
   │   │   ├── files/
   │   │   ├── tasks/
   │   │   └── templates/
   │   ├── playbooks/
   │   │   └── roles/
   │   ├── resources/
   │   └── secret/
   ├── ansible.cfg
   ├── .debops.cfg
   └── .gitignore

This is an example of a project directory after it was used to configure a few
hosts using DebOps roles and playbooks (some of the directory contents are
trimmed to make the result easier to read):

.. code-block:: none

   ~/src/projects/project1/
   ├── ansible/
   │   ├── collections/
   │   │   ├── ansible_collections/
   │   │   └── requirements.yml
   │   ├── inventory/
   │   │   ├── group_vars/
   │   │   │   ├── all/
   │   │   │   │   ├── apt.yml
   │   │   │   │   ├── keyring.yml
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
   │   ├── keyring/
   │   ├── overrides/
   │   │   ├── files/
   │   │   ├── tasks/
   │   │   └── templates/
   │   ├── playbooks/
   │   │   ├── deployment.yml
   │   │   └── roles/
   │   │       ├── service1/
   │   │       └── service2/
   │   ├── resources/
   │   │   ├── res-dir1/
   │   │   │   └── res-file1.zip
   │   │   └── res-dir2/
   │   │       └── res-file2.jpg
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
   ├── .git/
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


The "modern" directory layout
-----------------------------

This directory layout was created after a few years of experience with the
"legacy" layout. The design is based around a concept of "infrastructure
views", which translates to multiple Ansible inventories with separate secrets
and custom resources.

To create a project directory with this layout, you can issue the command:

.. code-block:: console

   debops project init --type modern ~/src/projects/project2

This command will create a directory structure with a set of default
configuration files used by :command:`git` and :command:`ansible`, which looks
something like this:

.. code-block:: none

   ~/src/projects/project2/
   ├── ansible/
   │   ├── collections/
   │   │   ├── ansible_collections/
   │   │   └── requirements.yml
   │   ├── keyring/
   │   ├── overrides/
   │   │   ├── files/
   │   │   ├── tasks/
   │   │   └── templates/
   │   └── views/
   │       └── system/
   │           ├── ansible.cfg
   │           ├── inventory/
   │           │   ├── group_vars/
   │           │   │   └── all/
   │           │   │       └── keyring.yml
   │           │   ├── hosts
   │           │   └── host_vars/
   │           ├── playbooks/
   │           │   └── roles/
   │           ├── resources/
   │           ├── secret/
   │           ├── .gitattributes
   │           └── .gitignore
   ├── .debops/
   │   ├── conf.d/
   │   │   ├── project.yml
   │   │   └── view-system.yml
   │   └── environment
   └── .gitignore

You can compare this with the "legacy" directory structure above. The important
changes with the previous layout are:

- DebOps configuration is now a :file:`.debops/conf.d/` directory within the
  project directory instead of a single file. It can contain files in JSON,
  TOML and YAML formats that are merged into a unified configuration structure.

- Parts of the project directory (Ansible inventory, custom resources, secrets)
  are moved into :file:`ansible/views/system/` subdirectory. The "system" view
  is meant to be used as the default privileged view for the infrastructure,
  with either ``root`` or other UNIX account with full :command:`sudo` access
  to the host.

Detailed description of each directory and file in the project directory can be
found further below.

.. _project_infrastructure_views:

How to use "infrastructure views"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The core concept of "infrastructure views" in a DebOps project directory is
meant to permit use of multiple Ansible inventories against a single
infrastructure. There are different ways to implement this in practice.

One example is to have a single Ansible inventory for privileged access to
hosts (the "system" view in the default configuration). This view is used by
system administrators to provision hosts, install system-wide software and
configure different layers of access control in parts of the system (access to
databases, filesystem ACLs and permissions, authentication services, and so
on). Other views can then be configured to use unprivileged access to parts of
the infrastructure, without going through :command:`sudo` which with Ansible
always requires full privileged access. For example, a deployment UNIX account
can have proper ACLs in the PostgreSQL service to create its own databases,
which still can be managed via Ansible tasks without issues.

Another way to utilize infrastructure views is to have a "production" view,
a "development" view and a "shared" view, which is included as an additional
inventory in both "production" and "development" inventories. In "production"
and "development" Ansible inventories users define hosts and access to them,
and in the "shared" Ansible inventory they define service groups and other
configuration. With this setup, Ansible configuration can be applied on the
"development" infrastructure, and when everything works OK, new configuration
can be deployed on "production" hosts without requiring any changes in
inventories. There might be more layers of inventories if needed, or
a blue-green deployment scheme if desired.

Infrastructure views can be defined in a hierarchical directory structure. For
example, you can have :file:`system` view as default, and then
:file:`deploy/app1` and :file:`deploy/app2` views for different applications.
Nesting a view inside of another view is disallowed to avoid security issues
and unpredictable Ansible behaviour. To see what views are defined in
a project, you can use the command:

.. code-block:: console

   debops config get -k views

The :command:`debops` script tries to automatically detect which
"infrastructure view" should be used - if the user has changed the current
directory to one under :file:`ansible/views/<view>/`, that particular view will
be used in various DebOps commands. Otherwise, the default view for a given
project will be used automatically. Users can override which view should be
used by specifying the ``-V <view>`` or ``--view <view>`` option in most of the
script commands. This also works outside of the project directory, when used
with the ``--project-dir <path>`` option. See the manual pages of different
DebOps commands to learn more.

The default view used by DebOps in a given project is defined in the
:file:`<project_dir>/.debops/conf.d/project.yml` configuration file, in the
``project.default_view`` configuration key. It can be set to an empty string;
in such case there will be no default view and it will have to be selected
using the ``-V <view>`` or ``--view <view>`` option on the command line.
Alternatively, users can :command:`cd` into a view subdirectory before
executing a :command:`debops` command to use it.

In the :file:`<project_dir>/.debops/conf.d/view-*.yml` configuration file
created for each "infrastructure view", users can select which Ansible
Collections will be searched for playbooks if one is specified without
a :file:`<namespace>.<collection>/`` prefix. This can be used to change the
default collection for a given "infrastructure view" to one which contains
unprivileged playbooks and roles, or add more Ansible Collections which should
be searched for playbooks.

.. _playbook_sets:

Per-view playbook sets
~~~~~~~~~~~~~~~~~~~~~~

Users can define "playbook sets" at the view level, using the
`views.<name>.playbook_sets` configuration option. This option is a YAML
dictionary with lists of playbooks to execute when a particular "playbook set"
is specified on the command line. An example configuration:

.. code-block:: yaml

   ---
   views:
     system:
       playbook_sets:
         'webservice':
           - 'layer/common'
           - 'service/nginx'
           - 'custom-app'

With the above configuration, users can execute a set of playbooks using the
command:

.. code-block:: console

   debops run webservice -l webserver

which will be internally expanded to:

.. code-block:: console

   debops run layer/common service/nginx custom-app -l webserver

After that, the usual playbook expansion will take place. The first two
playbooks will be found in the DebOps collection, and the :file:`custom-app`
playbook will be presumably in the :file:`ansible/views/system/playbooks/`
subdirectory of the project directory. If a potential playbook set is not found,
the argument will be expanded into a playbook if possible, or passed to the
:command:`ansible-playbook` command as-is.

This mechanism can be used to redefine existing playbooks into playbook sets.
For example, if users want to include additional playbooks in the "site"
playbook, they can:

.. code-block:: yaml

   ---
   views:
     system:
       playbook_sets:
         'site':
           - 'site'
           - '<namespace>.<collection>.custom_playbook'

Now calling the "site" playbook will execute the DebOps own :file:`site.yml`
playbook, and an additional playbook from a specific Ansible Collection.

Please remember that this feature does not modify the actual playbooks, just the
way they are called from the command line. This means that including the
:file:`site.yml` playbook in another playbook will run just that one playbook,
not all the playbooks defined in a playbook set.


DebOps and :command:`git` integration
-------------------------------------

Project directories are designed to be stored in :command:`git` repositories.
The repository will be initialized by default when a new project is created; to
avoid this users can use the `--no-git` parameter during project creation.

When :command:`git` repositories are configured with encrypted secrets, using
either EncFS or :command:`git-crypt`, the :command:`debops` script will by
default commit current contents of the project repository when certain actions
are performed. Currently, this happens when project secrets are unlocked or
locked - this is required by :command:`git-crypt` to work correctly (the
:command:`git` repository needs to be clean), but DebOps will do this for EncFS
as well, for consistency.

If the project secrets were unlocked manually, using the :command:`debops
project unlock` command, any changes done afterwards will be committed when the
secrets are locked again. This allows users to perform multiple changes in the
project directory and commit them by hand as they see fit.

Any commits done by DebOps automatically can be updated, for example to provide
a more extensive commit message. Users can use :command:`git rebase -i` command
to edit older commits; latest commit can be modified using the :command:`git
commit --amend` command.

Contents of the project directory
---------------------------------

Main Ansible configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`ansible.cfg`
:modern: :file:`ansible/views/<view>/ansible.cfg`

This is a configuration file read by the :command:`ansible` and
:command:`ansible-playbook` commands. This file is generated when the project
is initialized, but it's not stored in the :command:`git` version control to
avoid conflicts with paths on different Ansible Controllers.

The contents of this file are configured using the DebOps configuration system.
You can use the :command:`debops project refresh` command to update this file
or recreate it after the project directory is cloned from a :command:`git`
repository. Any changes in this file made directly will be lost, so it's best
to save them in DebOps configuration files after testing them.


Ansible Collection requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:both: :file:`ansible/collections/requirements.yml`

This file contains a `list of Ansible Collections`__ which are required by
DebOps or other parts of a given project. It can be edited and committed to
version control.

.. __: https://docs.ansible.com/ansible/latest/galaxy/user_guide.html#install-multiple-collections-with-a-requirements-file

If you installed Ansible using just the :command:`ansible-core` Python package,
without any collections included, you might need to install the listed
collections manually if they are not already available on your user account or
system-wide. To install these collections within the project directory, you can
run the command:

.. code-block:: console

   debops env ansible-galaxy collection install -r ansible/collections/requirements.yml

to download the listed collections and their dependencies. They will be
unpacked inside of the :file:`ansible/collections/ansible_collections/`
subdirectory and ignored by version control.

To see a list of installed collections, you can run the command:

.. code-block:: console

   debops env ansible-galaxy collection list


The Ansible inventory
~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`ansible/inventory/`
:modern: :file:`ansible/views/<view>/inventory/`

This is the directory where Ansible will look for its inventory. In the example
above, it's a static inventory based on an INI file format, however if you wish
you can switch it to a dynamic inventory generated from a database; just
replace the :file:`ansible/inventory/hosts` file with a script.

The inventory variables can be put either in a single file, or multiple files,
which might be more convenient if you want to share the same variables across
project directories using symlinks. Just remember that you cannot mix
directories and files on the same level of the inventory directory structure.

Better way to share variables across inventories might be to create a "shared"
inventory and specify the path to that inventory in the :file:`ansible.cfg`
configuration file.


Playbook and role directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`ansible/playbooks/roles/`
:modern: :file:`ansible/views/<view>/playbooks/roles/`

This is a set of directories that can hold Ansible playbooks and roles in the
project directory which are not part of an Ansible Collection. Each
"infrastructure view" has its own set of playbook and role directories, since
they are tied to that particular view's Ansible inventory and resulting access
control.


Data for :ref:`debops.resources` role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`ansible/resources/`
:modern: :file:`ansible/views/<view>/resources/`

This directory can be used to store various files which can be accessed by the
:ref:`debops.resources` Ansible role to copy them over to the remote hosts.


Data store for :ref:`debops.secret` role
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`ansible/secret/`
:modern: :file:`ansible/views/<view>/secret/`

This directory is maintained by the :ref:`debops.secret` Ansible role. You can
find there plaintext passwords, randomly generated by different roles, as well
as PKI configuration and some other data - the directory is sometimes used to
distribute public keys or other information between hosts via Ansible
Controller.


.. _global_vars:

Global variables passed to Ansible
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`ansible/global-vars.yml`
:modern: :file:`ansible/views/<view>/global-vars.yml`

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


DebOps configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~

:legacy: :file:`.debops.cfg`
:modern: :file:`.debops/conf.d/`

The :command:`debops` command is looking for this file for current directory to
see if it's a project directory; if it's not found the execution is aborted to
not cause issues in the filesystem.

This file contains configuration for some of the custom DebOps lookup plugins,
as well as configuration which should be added to the automatically generated
:file:`ansible.cfg` configuration file.


Persistent environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:both:   :file:`.env`
:modern: :file:`.debops/environment`

These files can contain environment variables which will be included in the
runtime environment in various :command:`debops` subcommands.


Overriding the ``site`` playbook
--------------------------------

The :file:`debops/ansible/playbooks/site.yml` playbook located in the DebOps
monorepo connects all debops roles.

By creating a playbook named :file:`ansible/playbooks/site.yml` inside your
project folder, you can override the debops version of :file:`site.yml`
and hook your role to the :command:`debops` command instead:

in :file:`ansible/playbooks/site.yml`:

.. code-block:: yaml

  ---
  - import_playbook: '{{ lookup("ENV", "HOME") + "/.local/share/debops/debops/ansible/playbooks/site.yml" }}'
  - import_playbook: your_role.yml


in :file:`ansible/playbooks/your_role.yml`:

.. code-block:: yaml

  ---
  - name: Manage your specific setup
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
