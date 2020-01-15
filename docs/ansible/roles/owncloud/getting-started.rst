.. _owncloud__ref_getting_started:

Getting started
===============

.. contents::
   :local:

.. include:: ../../../includes/global.rst
.. include:: includes/role.rst

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

If you are upgrading an existing Nextcloud installation, you should follow
`Enabling MySQL 4-byte support`__
and then set the following in your inventory of the database server:

.. __: https://docs.nextcloud.com/server/16/admin_manual/configuration_database/mysql_4byte_support.html

.. code-block:: yaml

   mariadb_server__options:
     - section: 'mysqld'
       options:

         ## https://docs.nextcloud.com/server/16/admin_manual/configuration_database/mysql_4byte_support.html
         'innodb_large_prefix': 'on'
         'innodb_file_format': 'barracuda'
         'innodb_file_per_table': 'true'

For database clean installs this is not required anymore because MySQL 4-byte
is enabled by default by the :ref:`debops.mariadb_server` Ansible role.


In memory caching
-----------------

Nextcloud and ownCloud recommend to setup Redis_ for caching. You can install a Redis server
on the same host as ownCloud or choose a different host:

.. code-block:: none

    [debops_service_redis_server]
    hostname

This role will use a Redis server automatically when it is managed by
:ref:`debops.redis_server` Ansible role.

In case you chose a different host, you will need to specify which of your
Redis servers the ownCloud instance should use by setting the Redis
server host as :envvar:`owncloud__redis_host` and setting
:envvar:`owncloud__redis_enabled` to ``True``.
Additionally, you will need to set the :envvar:`owncloud__redis_password`.
Refer to :ref:`debops.redis_server` documentation for details.

PHP configuration
-----------------

Starting with Nextcloud 16, a setup warning is emitted in the Nextcloud admin web interface "The PHP memory limit is below the recommended value of 512MB.". The role already configures Nginx to pass an increased memory_limit to PHP. However, this might not be picked up in some cases. When this happens you might want to set the following in your inventory:

.. code-block:: yaml

   php__ini_memory_limit: '512M'


.. _owncloud__ref_choosing_a_webserver:

Choosing a Webserver
--------------------

Supported webservers:

* Nginx_
* Apache_

This role started out using Nginx_ as Webserver. However, ownCloud_ and
NextCloud_ don’t officially support Nginx_. As of ``debops.owncloud`` v0.4.0,
support for the `Apache HTTP Server`_ has been added to the role using
:ref:`debops.apache` as role dependency.

The current default Webserver is Nginx_. Because despite the fact that only
Apache_ is officially supported, Nginx_ has been successfully used with this
role for some time now. If you have trouble with ownCloud then this would be a
good time to try to run it with Apache.

The `ownCloud System Requirements`_ don’t use PHP-FPM in their default
configuration. You can set the following in your inventory to not install FPM
on the ownCloud host:

.. code-block:: yaml

   php__server_api_packages:
     - 'cli'


Switching Webservers
--------------------

Assuming you where using one Webserver before on a host but want to switch then
follow the steps in `Choosing a Webserver`_ and additionally add the host to
the ``debops_service_${not_chosen_webserver}`` group of the opposite webserver
you chose for ownCloud.
Now add this:

.. code-block:: yaml

   ${not_chosen_webserver}__deploy_state: 'absent'

to your inventory.

Note: Replace the ``${not_chosen_webserver}`` placeholders.

Then run the site playbook or just the playbook of the unwanted webserver
followed by the debops.owncloud playbook.
This will render ``${not_chosen_webserver}`` the unwanted webserver harmless
and setup the chosen webserver.

Example inventory
-----------------

To setup ownCloud on a given host it should be included in the
``[debops_service_owncloud]`` Ansible inventory group:

.. code-block:: none

    [debops_service_owncloud]
    hostname

Note that the ``debops_service_owncloud`` group uses the default webserver,
refer to :ref:`owncloud__ref_choosing_a_webserver`.

.. _owncloud__ref_ansible_facts:

Ansible facts
-------------

The role gathers various Ansible facts about ownCloud for internal use or use
by other roles or playbooks.

One of the sources for the facts is the :file:`/var/www/owncloud/config/config.php`
file which has ``0640`` as default permissions.
The remote user who gathers the facts should be able to read this file.
Note that facts gathering does not happen with elevated privileges by default.
One way to achieve this is by making your configuration management user member
of the ``www-data`` group by including the following in your inventory:

.. code-block:: yaml

   bootstrap__admin_groups: [ 'admins', 'staff', 'adm', 'sudo', 'www-data' ]

The following Ansible facts are available:

.. code-block:: json

   {
       "auto_security_updates_enabled": false,
       "datadirectory": "/var/www/owncloud/data",
       "enabled": true,
       "instanceid": "xxxxxxxxxxxx",
       "maintenance": false,
       "release": "9.0",
       "theme": "debops",
       "trusted_domains": [
           "cloud.example.org"
       ],
       "updatechecker": false,
       "variant": "owncloud",
       "version": "9.0.7.1",
       "webserver": "nginx"
   }

Note that the role uses Ansible facts gathered from the :file:`config.php`
file internally and might not work as expected when those facts can not be gathered.

The following can happen when the configuration management user has no access
to the :file:`config.php` file:

* Certain :command:`occ` commands are not available in maintenance mode. The
  role normally filters those commands out if it detects that ownCloud is in
  maintenance mode. Maintenance mode is assumed to be off if it can not be
  detected. If it is on, role execution will stop when one of those
  :command:`occ` commands is encountered.

and only the following facts will be available in this case:

.. code-block:: json

   {
       "auto_security_updates_enabled": true,
       "enabled": true,
       "variant": "owncloud",
       "webserver": "nginx"
   }

Example playbook
----------------

The following playbooks are used in DebOps. If you are using these role without
DebOps you might need to adapt them to make them work in your setup.

Ansible playbook that uses the ``debops.owncloud`` role together with :ref:`debops.nginx`:

.. literalinclude:: ../../../../ansible/playbooks/service/owncloud-nginx.yml
   :language: yaml

Ansible playbook that uses the ``debops.owncloud`` role together with :ref:`debops.apache`:

.. literalinclude:: ../../../../ansible/playbooks/service/owncloud-apache.yml
   :language: yaml

These playbooks are shipped with DebOps and are also contained in this role under
:file:`docs/playbooks/`.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::owncloud``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::owncloud:pkg``
  Tasks related to system package management like installing, upgrading or
  removing packages.

``role::owncloud:tarball``
  Tasks related to installing by Tarball.

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
