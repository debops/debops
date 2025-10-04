.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents:: Sections
      :local:

Installation methods
--------------------

The default installation method will be using an upstream URL download. The
:ref:`debops.golang` manages the actual installation and provides an option to
install from the source code as well. You can use the
:envvar:`miniflux__upstream_type` variable to select the desired installation
method.

Miniflux requires the ``embed`` library, which was `introduced in Go 1.16`__.
Debian Bullseye comes with Go 1.15, therefore installation from source will not
be possible by default. Newer Go is available via the ``bullseye-backports``
repository, so it is possible to build Miniflux using the backported Golang
packages.

.. __: https://tip.golang.org/doc/go1.16#library-embed


Steps required after installation
---------------------------------

After Miniflux is installed, you should be able to access it on the
``miniflux.<domain>`` address through the web browser. The default address can
be defined using the :envvar:`miniflux__fqdn` variable.

To access the service, you will need to create the initial administrator
account (done interactively, so not automated at this point). To do that, you
have to login to the server, and using the ``root`` UNIX account run the
command:

.. code-block:: console

   miniflux -c /etc/miniflux.conf -create-admin

After providing an username and password, you can login to Miniflux using the
provided credentials via the web interface. Additional user accounts can be
created in the web UI.


Example inventory
-----------------

To install the Miniflux service on a host, it needs to be included in the
``[debops_service_miniflux]`` Ansible inventory group. You also need to
configure a PostgreSQL service as a backend, it can be deployed on the same or
a different host.

Example Ansible inventory:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_postgresql_server]
   hostname

   [debops_service_miniflux]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.miniflux`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/miniflux.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::miniflux``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
