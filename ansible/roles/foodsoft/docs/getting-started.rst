.. _foodsoft__ref_getting_started:

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Database support
----------------

It is recommended that you install a database server. You can install one on
the same host as Foodsoft or choose a different host:

.. code-block:: none

    [debops_service_mariadb_server]
    hostname

In case you chose a different host, you will need to specify which of your
database servers the Foodsoft instance should use by specifying the database
server host as :envvar:`foodsoft__database_server`.

Webserver support
-----------------

Currently, only Nginx_ is supported using debops.nginx_.

You will need to install Nginx_ with Passenger support by setting:

.. code-block:: yaml

   nginx_flavor: 'passenger'

in your inventory.


Example inventory
-----------------

To manage Foodsoft on a given host or set of hosts, they need to be added
to the ``[debops_service_foodsoft_nginx]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_foodsoft_nginx]
   hostname

   [debops_service_mariadb_server]
   hostname

Example playbook
----------------

Ansible playbook that uses the ``debops-contrib.foodsoft`` role together
with debops.nginx_:

.. literalinclude:: playbooks/foodsoft-nginx.yml
   :language: yaml

The playbook is shipped with this role under
:file:`./docs/playbooks/` from which you can symlink it to your
playbook directory.
In case you use multiple `DebOps Contrib`_ roles, consider using the
`DebOps Contrib playbooks`_.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::foodsoft``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::foodsoft:pkgs``
  Tasks related to system package management like installing or
  removing packages.

``role::foodsoft:config``
  Tasks related to configuring Foodsoft.
