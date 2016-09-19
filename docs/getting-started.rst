Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst

Database setup
--------------

It is recommended that you install a database server. You can install one on
the same host as ownCloud or choose a different host:

.. code-block:: none

    [debops_service_mariadb_server]
    hostname

In case you chose a different host, you will need to specify which of your
database servers the ownCloud instance should use by specifying the database
server host as :envvar:`owncloud__database_server`.

In memory caching
-----------------

ownCloud recommends to setup Redis_ for caching. You can install a Redis server
on the same host as ownCloud or choose a different host:

.. code-block:: none

    [debops_service_redis]
    hostname

This role will use a Redis server automatically when it is managed by
debops.redis_.

In case you chose a different host, you will need to specify which of your
Redis servers the ownCloud instance should use by setting the Redis
server host as :envvar:`owncloud__redis_host` and setting
:envvar:`owncloud__redis_enabled` to ``True``.
Additionally, you will need to set the :envvar:`owncloud__redis_password`.
Refer to debops.redis_ for details.

Example inventory
-----------------

To setup ownCloud on a given remote host, it needs to be added to
``[debops_service_owncloud]`` Ansible inventory group:

.. code-block:: none

    [debops_service_owncloud]
    hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.owncloud`` role:

.. literalinclude:: playbooks/owncloud.yml
   :language: yaml

This playbooks is shipped with DebOps and is also contained in this role under
:file:`docs/playbooks/owncloud.yml`.


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

``role::owncloud:pkg``
  Tasks related to system package management like installing, upgrading or
  removing packages.

``role::owncloud:config``
  Run tasks related to ownCloud configuration and setup.

``role::owncloud:mail``
  Run tasks related to the deployment of the mail configuration.

``role::owncloud:occ``
  Run tasks related to the :command:`occ` command.

``role::owncloud:occ_config``
  Run tasks related to :command:`occ config:` commands generated from
  :envvar:`owncloud__apps_config` variables.

``role::owncloud:auto_upgrade``
  Run tasks related preparing ownCloud auto upgrade.

``role::owncloud:ldap``
  Run tasks related to the LDAP configuration.

``role::owncloud:theme``
  Run tasks related to the configuring the ownCloud theme.

``role::owncloud:copy``
  Run tasks related to copying and deletion of files in user profiles.
