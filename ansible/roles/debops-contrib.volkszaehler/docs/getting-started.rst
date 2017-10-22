.. _volkszaehler__ref_getting_started:

Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Database support
----------------

It is recommended that you install a database server. You can install one on
the same host as volkszaehler or choose a different host:

.. code-block:: none

    [debops_service_mariadb_server]
    hostname

In case you chose a different host, you will need to specify which of your
database servers the volkszaehler instance should use by specifying the database
server host as :envvar:`volkszaehler__database_server`.

Webserver support
-----------------

The following two webservers are supported by the role:

* Apache_ using debops.apache_.
* Nginx_ using debops.nginx_.

The role maintainer has chosen Nginx as webserver for his deployments.
He added Apache support because he is very familiar with debops.apache_ (author).
Note that integration testing is done with debops.nginx_ only, currently.

In case you chose Apache, you don’t need PHP FPM which debops.php_ might
install by default.
To ensure that FPM is not going to be installed, add the following to your
inventory:

.. code-block:: yaml

   php__server_api_packages:
     - 'cli'

Example inventory
-----------------

To manage volkszaehler on a given host or set of hosts, they need to be added
to the ``[debops_service_volkszaehler_${webserver}]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_volkszaehler_apache]
   hostname

   [debops_service_mariadb_server]
   hostname

   [debops_service_volkszaehler_nginx]
   hostname2

Example playbook
----------------

Ansible playbook that uses the ``debops-contrib.volkszaehler`` role together
with debops.apache_:

.. literalinclude:: playbooks/volkszaehler-apache.yml
   :language: yaml

Ansible playbook that uses the ``debops-contrib.volkszaehler`` role together
with debops.nginx_:

.. literalinclude:: playbooks/volkszaehler-nginx.yml
   :language: yaml

These playbooks are shipped with this role under
:file:`./docs/playbooks/` from which you can symlink them to your
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

``role::volkszaehler:env``
  Environment role tag, should be used in the playbook to execute a special
  environment role contained in the main role. The environment role prepares
  the environment for other dependency roles to work correctly.

``role::volkszaehler``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::volkszaehler:pkgs``
  Tasks related to system package management like installing or
  removing packages.
