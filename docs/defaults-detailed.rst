Default variable details
========================

.. include:: includes/all.rst

Some of ``debops.resources`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

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

.. _resources__ref_urls:

resources__urls
---------------

These lists can be used to download online resources over HTTP, HTTPS or FTP
protocols. Each element of a list is a YAML dictionary with parameters. You can
use all parameters of the ``get_url`` Ansible module; see its documentation for
the parameter list and syntax.

To download resources over HTTPS, the content must be served over a valid
TLS/SSL certificate recognized by the remote host. If you use self-siged
certificates, check the ``debops.pki`` role for how to add custom Root CA
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

The ``resources__src`` variable can be used to point the role to a custom,
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

These lists can be used to manage content or copy files from Ansible Controller
to remote hosts. Each element of a list is a YAML dictionary with parameters
used by the `Ansible copy module`_. See its documentation for parameter usage
and syntax.

The ``resources__src`` variable can be used to point the role to a custom,
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
  Optional. If not specified, or if specified and ``present``, file will be
  created. If specified and ``absent``, file will be removed.

Examples
~~~~~~~~

Copy file from the ``ansible/resources/`` directory to all remote hosts:

.. code-block:: yaml

   resources__files:
     - src: '{{ resources__src + "path/to/file" }}'
       dest: '/tmp/file'

Create a custom ``cron`` task that restarts a service daily:

.. code-block:: yaml

   resources__host_files:
     - dest: '/etc/cron.daily/service-restart'
       mode: '0755'
       content: |
         #!/bin/sh
         # {{ ansible_managed }}
         test -x /usr/bin/service && systemctl restart service

