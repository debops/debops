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

Examples
~~~~~~~~

Clone the Ansible repository to the host:

.. code-block:: yaml

   resources__repositories:
     - repo: 'https://github.com/ansible/ansible'
       dest: '/usr/local/src/github.com/ansible/ansible'


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
