Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.resources`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _resources__ref_templates:

resources__templates
--------------------

The :ref:`debops.resources` role supports dynamic generation of directories,
templated files and symlinks using the `with_filetree`__ Ansible lookup plugin.

.. __: https://docs.ansible.com/ansible/2.5/plugins/lookup/filetree.html

The file, directory and symlink management is limited - the managed resources
will be owned by ``root`` UNIX account and will be placed in the ``root`` UNIX
group, however the specific file mode will be preserved; for example if you
create a file with ``0600`` permissions, the same permissions will be set by
the role on the remote host. You can use the :ref:`resources__ref_paths`
functionality to modify file/directory ownership afterwards.

.. warning::

   The task ensures that each directory in the path exists, including
   permissions. You have to set specific permissions for certain directories
   like :file:`/root` (``0700``) or :file:`/tmp` (``1777``)  in order to not
   modify them in unexpected manner.

For this functionality to work, the role expects a specific directory structure
located in the :file:`ansible/resources/` directory (or wherever the
:envvar:`resources__src` variable points to):

.. code-block:: none

   ansible/resources/
   └── templates/
       ├── by-group/
       │   ├── all/
       │   ├── group-name1/
       │   └── group-name2/
       └── by-host/
           ├── hostname1/
           └── hostname2/

The ``with_filetree`` Ansible lookup plugin will look for resources to manage
in specific hostname directory, then of all the groups the current host is in
(based on the content of the variable `group_names`), then in the :file:`by-group/all/` directory.
The resource found first in this order wins and no further checks
are performed; this means that you can put a file in the :file:`by-group/all/`
directory and then override it using a host-specific directory.
The groups directories are read in the order dictated by Ansible during inventory parsing.

See `Ansible - Playbooks Variables`__ to learn about the ``group_names`` variable, and `Ansible - Working with Inventory`__

.. __: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#accessing-information-about-other-hosts-with-magic-variables
.. __: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#how-variables-are-merged

for more information on how to use ``ansible_group_priority`` to change the merge order
for groups of the same level (after the parent/child order is resolved).

Each directory structure starts at the root of the filesystem (:file:`/`), so
to create a file in a subdirectory you need to recreate the entire path. For
example, to create the :file:`/var/lib/application/custom.txt` file, it needs
to be placed in:

.. code-block:: none

   ansible/resources/templates/by-group/all/var/lib/application/custom.txt

In the templates, you can reference variables from the Ansible facts (including
local facts managed by other roles) and Ansible inventory. Referencing
variables from other roles might work only if these roles are included in the
playbook, however that is not idempotent and should be avoided.

.. _resources__ref_paths:

resources__paths
----------------

These lists can be used to create directories, symlinks, set permissions and
ownership, etc. Each element of the list is a YAML dictionary with a set of
parameters. See the documentation of the `Ansible file module`_ for details
about what parameters can be used and their format. Here's are additional
details for certain parameters:

``item.path`` or ``item.dest`` or ``item.name``
  Specify absolute path of the target directory/file on the remote host. If not
  specified, the entire entry is treated as a directory path.

``item.state``
  Optional. Specify state of the given path. If not specified, the element is
  treated as a directory which will be created if it doesn't exist.

``item.acl``
  Optional. Please take a look :ref:`resources__ref_acl` section.

``item.access_time`` and ``item.modification_time``
  Optional. As documented by the `Ansible file module`_ except that DebOps
  defines a more human readable and standard compliant format.
  Example: ``2023-05-23T23:42:42``

``item.access_time_format`` and ``item.modification_time_format``
  Optional. If not defined, it defaults to :envvar:`resources__time_format`.

Examples
~~~~~~~~

Create a set of directories on all hosts:

.. code-block:: yaml

   resources__paths:
     - '/tmp/dir1'
     - '/tmp/dir2'

Create a public WWW directory on the user account and symlink it to the webroot
directory served by the HTTP server:

.. code-block:: yaml

   resources__host_paths:
     - path: '/home/user1/public'
       owner: 'user1'
       group: 'user1'
       mode: '0755'

     - path: '/srv/www/sites/example.com'
       state: 'directory'

     - path: '/srv/www/sites/example.com/public'
       src:  '/home/user1/public'
       state: 'link'

Remove specified path:

.. code-block:: yaml

   resources__paths:
     - path: '/tmp/removed'
       state: 'absent'


.. _resources__ref_repositories:

resources__repositories
-----------------------

These lists can be used to clone or update remote :command:`git` repositories.
You can use all parameters of the :command:`git` Ansible module to manage the
repositories, with some exceptions. The role recognizes these additional
parameters:

``item.repo``, ``item.url`` or ``item.src``
  Required. The URL of the :command:`git` repository to clone..

``item.dest`` or ``item.name`` or ``item.path``
  Required. Path where the specified repository should be cloned to.

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
  permissions allow. You can create or change directory permissions as needed
  using the :ref:`resources__ref_paths` variables.

``item.acl``
  Optional. Please take a look :ref:`resources__ref_acl` section.

Examples
~~~~~~~~

Clone the Ansible repository to the host:

.. code-block:: yaml

   resources__repositories:
     - repo: 'https://github.com/ansible/ansible'
       dest: '/usr/local/src/github.com/ansible/ansible'

Clone a private repository, accessible using a SSH key. The UNIX account
specified as the owner, or ``root`` account when otherwise, needs to have the
SSH key accepted by the repository. This example uses `Gitea`__ instance as the
source of the :command:`git` repository:

.. __: https://gitea.io/

.. code-block:: yaml

   resources__repositories:
     - repo: 'ssh://git@git.example.org:29418/namespace/repository.git'
       owner: 'username'
       dest: '~username/src/git.example.org/namespace/repository'
       accept_hostkey: True


.. _resources__ref_urls:

resources__urls
---------------

These lists can be used to download online resources over HTTP, HTTPS or FTP
protocols. Each element of a list is a YAML dictionary with parameters. You can
use all parameters of the ``get_url`` Ansible module; see its documentation for
the parameter list and syntax.

To download resources over HTTPS, the content must be served over a valid
TLS/SSL certificate recognized by the remote host. If you use self-signed
certificates, check the :ref:`debops.pki` for how to add custom Root CA
Certificates on your hosts.

Here are some important parameters used by the role:

``item.url`` or ``item.src``
  Required. The URL of the resource to download.

``item.dest`` or ``item.name`` or ``item.path``
  Required. Path where downloaded resource should be stored.

``item.acl``
  Optional. Please take a look :ref:`resources__ref_acl` section.

Examples
~~~~~~~~

Download a HTML file from a webserver on all hosts:

.. code-block:: yaml

   resources__urls:
     - src: 'http://www.example.com/page.html'
       dest: '/tmp/page.html'

.. _resources__ref_archives:

resources__archives
-------------------

These lists can be used to unpack archives located on Ansible Controller to
remote hosts. Each element of the list is a YAML dictionary with parameters
recognized by the `Ansible unarchive module`_. For details about their use,
see the module documentation.

The :envvar:`resources__src` variable can be used to point the role to a custom,
central location, by default located in the DebOps project directory.

Here are some more important parameters:

``item.src``
  Required. Path to the archive located on Ansible Controller.

``item.dest`` or ``item.name`` or ``item.path``
  Required. Path on the remote host where the archive should be unpacked.

``item.acl``
  Optional. Please take a look :ref:`resources__ref_acl` section.

Examples
~~~~~~~~

Unpack the home directory contents of a particular user on a specific host. The
tarball is located at ``ansible/resources/home.tar`` on the Ansible Controller,
in DebOps project directory:

.. code-block:: yaml

   resources__host_archives:
     - src: '{{ resources__src + "home.tar" }}'
       dest: '/home/user'
       owner: 'user'
       group: 'user'

.. _resources__ref_files:

resources__files
----------------

These lists can be used to manage content or copy files from the Ansible
Controller to remote hosts. Each element of a list is a YAML dictionary with
parameters used by the `Ansible copy module`_. See its documentation for
parameter advanced usage and syntax.

The :envvar:`resources__src` variable can be used to point the role to a custom,
central location, by default located in the DebOps project directory.

Here are some more important parameters:

``item.dest`` or ``item.name`` or ``item.path``
  Required. Path to the destination file on the remote host.

``item.src``
  Path to the source file on the Ansible Controller. Alternatively you can use
  ``item.content`` to provide the file contents directly in the inventory.

``item.content``
  String or YAML text block with the file contents to put in the destination
  file. Alternatively you can use ``item.src`` to provide the path to the
  source file on Ansible Controller.

``item.state``
  Optional. If not specified, or if specified and ``present``, the file(s) will
  be created. If specified and ``absent``, file will be removed.

``item.acl``
  Optional. Please take a look :ref:`resources__ref_acl` section.

Examples
~~~~~~~~

Copy file from the :file:`ansible/resources/` directory to all remote hosts:

.. code-block:: yaml

   resources__files:
     - src: '{{ resources__src + "path/to/file" }}'
       dest: '/tmp/file'

Create a custom :program:`cron` task that restarts a service daily:

.. code-block:: yaml

   resources__host_files:
     - dest: '/etc/cron.daily/service-restart'
       mode: '0755'
       content: |
         #!/bin/sh
         # {{ ansible_managed }}
         test -x /usr/bin/service && systemctl restart service

.. _resources__ref_acl:

ACL support
-----------

Some of :ref:`debops.resources` variables also have the possibility to manage
the ACLs (:ref:`resources__ref_paths`, :ref:`resources__ref_repositories`,
:ref:`resources__ref_urls`, :ref:`resources__ref_archives` and
:ref:`resources__ref_files`).

Examples
~~~~~~~~

Create a directory on all hosts and allow ``adm`` group to access to any
new content:

.. code-block:: yaml

   resources__paths:
     - dest: '/tmp/dir1'
       acl:
         - default: True
           etype: 'group'
           entity: 'adm'
           permissions: 'rX'
         - default: True
           etype: 'user'
           entity: 'joe'
           permissions: 'rX'

Remove ACLs related to ``joe`` user on a file on all hosts:

.. code-block:: yaml

   resources__files:
     - dest: '/tmp/file'
       state: 'present'
       acl:
         - etype: 'user'
           entity: 'joe'
           state: 'absent'

Parameters related to ACL
~~~~~~~~~~~~~~~~~~~~~~~~~

``item.acl``
  Optional. Configure filesystem ACL entries of the current file or directory.
  This parameter is a list of YAML dictionaries. See the documentation of the
  `Ansible acl module`_ for details about each parameters (what they can be
  used to and their format) as well as the :man:`acl(5)`, :man:`setfacl(1)`
  and :man:`getfacl` manual pages. Some useful parameters:

  ``default``
    Optional, boolean. If ``True``, set a given ACL entry as the default for
    new files and directories inside a given directory. Only works with
    directories and can't be removed with ``state`` set to ``absent``.

  ``entity``
    Name of the UNIX user account or group that a given ACL entry applies to.

  ``etype``
    Specify the ACL entry type to configure. Valid choices: ``user``,
    ``group``, ``mask``, ``other``.

  ``permissions``
    Specify the permission to apply for a given ACL entry. This parameter
    cannot be specified when the state of an ACL entry is set to ``absent``.

  ``recursive``
    Apply a given ACL entry recursively to all entities in a given path.

  ``state``
    Optional. If not specified or ``present``, the ACL entry will be created.
    If ``absent``, the ACL entry will be removed. The ``query`` state doesn't
    make sense in this context and shouldn't be used.


.. _resources__ref_commands:

resources__commands
-------------------

The ``resources__*_commands`` variables can be used to define shell commands or
small scripts which should be executed on the remote hosts. This can be useful
to, for example, start a :command:`systemd` service created previously using
the :ref:`resources__ref_files` variables.

This is not a replacement for a fully-fledged Ansible role. The interface is
extremely limited, and you need to ensure idempotency inside of the script or
command you are executing. The :ref:`debops.resources` role can be executed at
different points in the main playbook, which you should also take into account.

Examples
~~~~~~~~

Set up a simple example :command:`systemd` service and start it:

.. code-block:: yaml

   resources__files:
     - content: |
         [Unit]
         Description=Example Service

         [Service]
         Type=simple
         ExecStart=/bin/true
         RemainAfterExit=yes

         [Install]
         WantedBy=multi-user.target
       dest: '/etc/systemd/system/example.service'
       mode: '0644'

   resources__commands:
     - name: 'Reload systemd and start example service'
       shell: |
         if ! systemctl is-active example.service ; then
             systemctl daemon-reload
             systemctl start example.service
         fi

Syntax
~~~~~~

Each shell command entry is defined by a YAML dictionary with specific
parameters:

``name``
  Required. A name of a given shell command displayed during Ansible execution,
  not used for anything else in the task. Multiple configuration entries with
  the same ``name`` parameter are merged together.

``script`` / ``shell`` / ``command``
  Required. String or YAML text block that contains the command or script to
  execute on the remote host. The contents will be passed to the ``shell``
  Ansible module.

``chdir``
  Optional. Specify the path to the directory on the remote host where the
  script should be executed.

``creates``
  Optional. Specify the path of the file on the remote host - if it's present,
  the ``shell`` module will not execute the script.

``removes``
  Optional. Specify the path of the file on the remote host - if it's absent,
  the ``shell`` module will not execute the script.

``executable``
  Optional. Specify the command interpreter to use. If not specified,
  ``/bin/bash`` will be used by default.

``state``
  Optional. If not specified or ``present``, the shell command will be executed
  as normal by the role. If ``absent``, the shell command will not be executed
  by the role. If ``ignore``, the configuration entry will not be evaluated by
  the role during execution. This can be used to conditionally activate and
  deactivate different shell commands on the Ansible level.

``no_log``
  Optional, boolean. If ``True``, Ansible will not display the task contents or
  record them in the log. It's useful to avoid recording sensitive data like
  passwords.
