Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To setup ownCloud on a given remote host, it needs to be added to
``[debops_service_owncloud]`` Ansible inventory group:

.. code-block:: none

    [debops_service_owncloud]
    hostname

Additionally it is recommended that you install a database server. You can
install one on the same host as ownCloud or choose a different host:

.. code-block:: none

    [debops_service_mariadb_server]
    hostname

In case you chose a different host, you will need to specify which of your
database servers the ownCloud instance should use by specifying the database
server host as ``owncloud_database_server``.

Example playbook
----------------

Here's an example playbook that can be used to manage ownCloud:

.. literalinclude:: playbooks/owncloud.yml
   :language: yaml

This playbooks is shipped with this role under
:file:`docs/playbooks/owncloud.yml` from which you can symlink it to your
playbook directory.


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::owncloud``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::owncloud:base_install``
  Run tasks related to the installation the ownCloud packages.
  FIXME: Rename to install

``role::owncloud:configure``
  Run tasks related to ownCloud configuration and setup.
  FIXME: Rename to setup

``role::owncloud:mail``
  Run tasks related to the deployment of the mail configuration.

``role::owncloud:custom_config``
  Run tasks related to the deployment of the custom configuration.

``role::owncloud:occ``
  Run tasks related to the :command:`occ` command.

``role::owncloud:ldap``
  Run tasks related to the LDAP configuration.
