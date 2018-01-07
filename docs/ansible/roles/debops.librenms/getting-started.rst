Getting started
===============

.. contents::
   :local:

LibreNMS configuration
----------------------

LibreNMS requires a MariaDB/MySQL database server. You can configure
one using ``debops.mariadb_server`` and ``debops.mariadb``, either on the
same host as LibreNMS, or remotely.

The SNMP protocol is used to gather metrics from devices. Network switches / routers should
have an option to enable SNMP in their configuration, on Debian hosts you can use the
``debops.snmpd`` role to install and configure ``snmpd`` service.
The ``debops.librenms`` role will automatically use the username and password created
by the ``debops.snmpd`` role as SNMP v3 credentials.

LLDP/xDP protocol is used for device autodiscovery and network map generation.
The ``debops.snmpd`` role will automatically install a suitable LLDP daemon for you.
If you enable SNMP/LLDP on the LibreNMS host as well as other hosts, after
installation LibreNMS should automatically detect and add nearby devices when
it adds its own host to the database.

After installation, the LibreNMS webpage should be available at the ``nms.`` subdomain.

You can access the LibreNMS CLI commands by switching to the ``librenms`` system
user, for example via ``sudo``. You can find the installation in
the ``~/sites/public`` directory by default.

Useful variables
----------------

This is a list of role variables which you are most likely want to define in
Ansible’s inventory to customize LibreNMS:

``librenms__snmp_communities``
  List of SNMP v1/v2c communities LibreNMS should use to authenticate to
  network devices. By default it contains the community ``public``.

``librenms__admin_accounts``
  List of admin accounts created in the LibreNMS database. Passwords are stored
  automatically in the ``secret/`` directory, see the ``debops.secret`` role for more
  details. By default an admin account based on the ``ansible_user`` variable
  is created.

``librenms__devices``
  List of devices to add to the LibreNMS database. Specify FQDN hostnames or IP
  addresses. By default LibreNMS will add its own host, based on
  the ``ansible_fqdn`` variable.

Example inventory
-----------------

To install and configure LibreNMS on a host, you need to add the host to the
``[debops_service_librenms]`` Ansible host group::

    [debops_service_librenms]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops.librenms`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/librenms.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after the host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::librenms``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::librenms:source``
  Clone or pull latest changes from LibreNMS repository.

``role::librenms:config``
  Run tasks related to LibreNMS configuration, including ``~/.snmp/snmp.conf``,
  ``config.php``, creation of admin accounts and device discovery.

``role::librenms:database``
  Configure and initialize LibreNMS database.

``role::librenms:snmp_conf``
  Update ``~/.snmp/snmp.conf`` configuration files.

``role::librenms:admins``
  Create missing LibreNMS admin accounts.

``role::librenms:devices``
  Add missing devices to LibreNMS database.
