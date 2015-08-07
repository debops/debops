Getting started
===============

.. contents::
   :local:

LibreNMS configuration
----------------------

LibreNMS requires a MariaDB/MySQL server for its database. You can configure
one using ``debops.mariadb_server`` and ``debops.mariadb`` roles, either on the
same host as LibreNMS, or remotely.

SNMP protocol is used to gather metrics from devices. Network switches / routers should
have an option to enable SNMP in their interface, on Debian hosts you can use
``debops.snmpd`` role to install and configure ``snmpd`` service.
``debops.librenms`` role will automatically use username and password created
by ``debops.snmpd`` role for SNMP v3 credentials.

LLDP/xDP protocol is used for device autodiscovery and network map generation.
``debops.snmpd`` role will automatically install suitable LLDP daemon for you.
If you enable SNMP/LLDP on LibreNMS host as well as other hosts, after
installation LibreNMS should automatically detect and add nearby devices when
it adds its own host to the database.

After installation, LibreNMS webpage should be available at ``nms.`` subdomain.

You can access the LibreNMS CLI commands by switching to ``librenms`` system
user, for example via ``sudo``. You can find the installation in
``~/sites/public`` directory by default.

Useful variables
----------------

This is a list of role variables which your most likely want to define in
Ansible inventory to customize LibreNMS:

``librenms_snmp_communities``
  List of SNMP v1/v2c communities LibreNMS should use to authenticate to
  network devices. By default contains ``public`` community.

``librenms_admin_accounts``
  List of admin accounts created in LibreNMS database. Passwords are stored
  automatically in ``secret/`` directory, see ``debops.secret`` role for more
  details. By default an admin account based on ``ansible_ssh_user`` variable
  is created.

``librenms_devices``
  List of devices to add to LibreNMS database. Specify FQDN hostnames or IP
  addresses. By default LibreNMS will add its own host, based on
  ``ansible_fqdn`` variable.

Example inventory
-----------------

To install and configure LibreNMS on a host, it you be added in the
``[debops_librenms]`` Ansible host group::

    [debops_librenms]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.librenms`` role::

    ---
    - name: Configure LibreNMS
      hosts: debops_librenms

      roles:

        - role: debops.librenms
          tags: [ 'role::librenms' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::librenms``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::librenms``
  Execute all ``debops.librenms`` role dependencies in its context.

``depend::mariadb:librenms``
  Run ``debops.mariadb`` dependent role in ``debops.librenms`` context.

``depend::php5:librenms``
  Run ``debops.php5`` dependent role in ``debops.librenms`` context.

``depend::nginx:librenms``
  Run ``debops.nginx`` dependent role in ``debops.librenms`` context.

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

