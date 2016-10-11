.. _owncloud__ref_getting_started:

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

.. _owncloud__ref_choosing_a_webserver:

Choosing a Webserver
--------------------

Supported webservers:

* Nginx_
* Apache_

This role started out using Nginx_ as Webserver. However, ownCloud_ and
NextCloud_ don’t officially support Nginx_. As of ``debops.owncloud`` v0.4.0,
support for the `Apache HTTP Server`_ has been added to the role using
``debops.apache`` as role dependency.

The current default Webserver is Nginx_. Because despite the fact that only
Apache_ is officially supported, Nginx_ has been successfully used with this
role for some time now. If you have trouble with ownCloud then this would be a
good time to try to run it with Apache.

The `ownCloud System Requirements`_ don’t use PHP-FPM in there default
configuration. You can set the following in your inventory to not install FPM
on the ownCloud host:

.. code-block:: yaml

   php__server_api_packages:
     - 'cli'


Switching Webservers
--------------------

Assuming you where using one Webserver before on a host but want to switch then
follow the steps in `Choosing a Webserver`_ and additionally add the host to
the ``debops_service_$webserver`` group of the opposite webserver you chose for
ownCloud.
Now add this:

.. code-block:: yaml

   $webserver__deploy_state: 'absent'

to your inventory and run the playbook of ``$webserver`` to remove the unwanted
webserver.

Note: Replace the ``$webserver`` placeholders.

Then run the site playbook or just the playbook of the unwanted webserver
followed by the playbook.

Example inventory
-----------------

To setup ownCloud on a given host it should be included in the
``[debops_service_owncloud]`` Ansible inventory group:

.. code-block:: none

    [debops_service_owncloud]
    hostname

Note that the ``debops_service_owncloud`` group uses the default webserver,
refer to :ref:`owncloud__ref_choosing_a_webserver`.

Example playbook
----------------

The following playbooks are used in DebOps. If you are using these role without
DebOps you might need to adapt them to make them work in your setup.

Ansible playbook that uses the ``debops.owncloud`` role together with ``debops.nginx``:

.. literalinclude:: playbooks/owncloud-nginx.yml
   :language: yaml

Ansible playbook that uses the ``debops.owncloud`` role together with ``debops.apache``:

.. literalinclude:: playbooks/owncloud-apache.yml
   :language: yaml

These playbooks are shipped with DebOps and are also contained in this role under
:file:`docs/playbooks/`.

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
