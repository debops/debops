.. _role_index:

DebOps role index
=================

This is a curated index of DebOps roles, categorized by their type and purpose.
Roles that are not linked don't have complete documentation available, or are
not yet integrated in DebOps.

.. include:: ../includes/global.rst

.. contents:: Role categories
   :local:


Applications
------------

These applications are visible to the end users. Application roles included in
DebOps are used to provide useful services in the data center environment, and
act as integration tests for other roles that manage webservers, databases,
etc.

- :ref:`debops.dokuwiki`
- :ref:`debops.etherpad`
- :ref:`debops.gitlab`
- :ref:`debops.kibana`
- :ref:`debops.librenms`
- :ref:`debops.mailman`
- :ref:`debops.netbox`
- :ref:`debops.owncloud`
- :ref:`debops.rstudio_server`
- :ref:`debops.prosody`
- ``debops.phpipam``
- ``debops.phpmyadmin``
- ``debops-contrib.foodsoft``
- ``debops-contrib.homeassistant``
- ``debops-contrib.kodi``


Application environments
------------------------

Ansible roles that are designed to help with installation of various
application environments or programming languages, either via APT or other
methods.

- :ref:`debops.apt_install`
- :ref:`debops.apt_preferences`
- :ref:`debops.cran` - `The Comprehensive R Archive Network`_
- :ref:`debops.elastic_co` - `Elastic`_ applications
- :ref:`debops.golang`
- :ref:`debops.hashicorp` - `HashiCorp`_ applications
- :ref:`debops.java`
- :ref:`debops.nodejs`
- :ref:`debops.php`
- :ref:`debops.ruby`
- ``debops.hwraid``
- ``debops.rails_deploy``
- ``debops-contrib.neurodebian``


Application services
--------------------

These roles manage applications that provide services to other applications and
are not accessed directly by end users.

- :ref:`debops.apt_cacher_ng`
- :ref:`debops.debops` - install DebOps on other hosts
- :ref:`debops.debops_api`
- :ref:`debops.gitlab_runner`
- :ref:`debops.fcgiwrap`
- :ref:`debops.gunicorn`
- :ref:`debops.memcached`
- :ref:`debops.mosquitto`
- :ref:`debops.rabbitmq_management`
- :ref:`debops.rabbitmq_server`
- :ref:`debops.salt`
- ``debops.reprepro``
- ``debops.sks``
- ``debops.smstools``
- ``debops-contrib.bitcoind``
- ``debops-contrib.volkszaehler``
- ``debops-contrib.x2go_server``


Backup
------

- :ref:`debops.rsnapshot`
- ``debops.boxbackup``


Databases
---------

- :ref:`debops.elasticsearch`
- :ref:`debops.mariadb`
- :ref:`debops.mariadb_server`
- :ref:`debops.postgresql`
- :ref:`debops.postgresql_server`
- :ref:`debops.redis`
- :ref:`debops.slapd`
- ``debops.phpmyadmin``


Encryption
----------

- :ref:`debops.cryptsetup`
- :ref:`debops.dhparam`
- :ref:`debops.pki`


Filesystems
-----------

Ansible roles that manage filesystem-level services, or export filesystems to
other hosts.

- :ref:`debops.cryptsetup`
- :ref:`debops.iscsi`
- :ref:`debops.lvm`
- :ref:`debops.nfs`
- :ref:`debops.nfs_server`
- :ref:`debops.persistent_paths`
- :ref:`debops.tftpd`
- :ref:`debops.tgt`
- ``debops.samba``
- ``debops-contrib.btrfs``
- ``debops-contrib.fuse``
- ``debops-contrib.snapshot_snapper``


Host provisioning
-----------------

- :ref:`debops.bootstrap`
- :ref:`debops.grub`
- :ref:`debops.ipxe`
- :ref:`debops.preseed`
- :ref:`debops.tftpd`
- ``debops-contrib.dropbear_initramfs``


Kernel
------

- :ref:`debops.sysctl`
- :ref:`debops.sysfs`
- ``debops-contrib.kernel_module``


Logging
-------

- :ref:`debops.elasticsearch`
- :ref:`debops.kibana`
- :ref:`debops.logrotate`
- :ref:`debops.rsyslog`


Mail services
-------------

- :ref:`debops.dovecot`
- :ref:`debops.etc_aliases`
- :ref:`debops.mailman`
- :ref:`debops.nullmailer`
- :ref:`debops.opendkim`
- :ref:`debops.postconf`
- :ref:`debops.postfix`
- :ref:`debops.postscreen`
- :ref:`debops.postwhite`
- :ref:`debops.saslauthd`
- ``debops.smstools``


Monitoring
----------

- :ref:`debops.librenms`
- :ref:`debops.monit`
- :ref:`debops.snmpd`
- ``debops.smstools``


Networking
----------

- :ref:`debops.avahi`
- :ref:`debops.dhcpd`
- :ref:`debops.dnsmasq`
- :ref:`debops.ifupdown`
- :ref:`debops.radvd`
- :ref:`debops.stunnel`
- :ref:`debops.tinc`
- :ref:`debops.unbound`
- ``debops-contrib.tor``


Operating system packages
-------------------------

Configuration of the APT package manager, automatic upgrades of installed
packages.

- :ref:`debops.apt`
- :ref:`debops.apt_cacher_ng`
- :ref:`debops.apt_listchanges`
- :ref:`debops.apt_install`
- :ref:`debops.apt_preferences`
- :ref:`debops.apt_proxy`
- :ref:`debops.unattended_upgrades`
- ``debops.reprepro``


Security
--------

- :ref:`debops.auth`
- :ref:`debops.authorized_keys`
- :ref:`debops.fail2ban`
- :ref:`debops.ferm`
- :ref:`debops.sshd`
- :ref:`debops.tcpwrappers`
- ``debops-contrib.apparmor``
- ``debops-contrib.firejail``


System configuration
--------------------

- :ref:`debops.atd`
- :ref:`debops.cron`
- :ref:`debops.environment`
- :ref:`debops.etc_services`
- :ref:`debops.ferm`
- :ref:`debops.locales`
- :ref:`debops.logrotate`
- :ref:`debops.machine`
- :ref:`debops.nsswitch`
- :ref:`debops.ntp`
- :ref:`debops.resources`
- :ref:`debops.root_account`
- :ref:`debops.swapfile`
- :ref:`debops.sysctl`
- :ref:`debops.sysfs`
- :ref:`debops.users`
- ``debops.console``
- ``debops.gitusers``
- ``debops.sftpusers``
- ``debops-contrib.etckeeper``


Web services
------------

- :ref:`debops.apache`
- :ref:`debops.fcgiwrap`
- :ref:`debops.gunicorn`
- :ref:`debops.nginx`
- :ref:`debops.nodejs`
- :ref:`debops.php`


Virtualization
--------------

- :ref:`debops.docker`
- :ref:`debops.docker_gen`
- :ref:`debops.libvirt`
- :ref:`debops.libvirtd`
- :ref:`debops.libvirtd_qemu`
- :ref:`debops.lxc`
- ``debops.openvz``


Ansible internals
-----------------

These Ansible roles are used internally during playbook execution, or provide
additional functions to other roles.

- :ref:`debops.ansible_plugins`
- :ref:`debops.core`
- :ref:`debops.debops_fact`
- :ref:`debops.secret`
