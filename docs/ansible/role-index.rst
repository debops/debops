.. Copyright (C) 2017-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _role_index:

Roles (by category)
===================

This is a curated index of DebOps roles, categorized by their type and purpose.
Roles that are not linked don't have complete documentation available, or are
not yet integrated in DebOps.

See also `DebOps roles in development`__ and `open pull requests`__.

  .. __: https://github.com/debops/debops/wiki/DebOps-roles-in-development
  .. __: https://github.com/debops/debops/pulls?q=is%3Aopen+is%3Apr+label%3A%22new+feature%22

.. include:: ../includes/global.rst

.. contents:: Role categories
   :local:

.. The categories below are also used in ../../CODEOWNERS.
   Please review and update this file if you make changes here.

.. TODO: Each role can only be in one category.

Applications
------------

These applications are visible to the end users. Application roles included in
DebOps are used to provide useful services in the data center environment, and
act as integration tests for other roles that manage webservers, databases,
etc.

- :ref:`debops.dokuwiki`
- :ref:`debops.etesync`
- :ref:`debops.etherpad`
- :ref:`debops.gitlab`
- :ref:`debops.icinga`
- :ref:`debops.kibana`
- :ref:`debops.librenms`
- :ref:`debops.mailman`
- :ref:`debops.minidlna`
- :ref:`debops.netbox`
- :ref:`debops.owncloud`
- :ref:`debops.phpipam`
- :ref:`debops.prosody`
- :ref:`debops.roundcube`
- :ref:`debops.rstudio_server`
- ``debops.phpmyadmin``
- ``debops-contrib.foodsoft``
- ``debops-contrib.homeassistant``
- ``debops-contrib.kodi``
- ``debops-contrib.volkszaehler``


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
- :ref:`debops.influxdata` - `InfluxData`_ applications
- :ref:`debops.java`
- :ref:`debops.neurodebian`
- :ref:`debops.nodejs`
- :ref:`debops.php`
- :ref:`debops.python`
- :ref:`debops.ruby`
- :ref:`debops.wpcli`
- ``debops.hwraid``
- ``debops.rails_deploy``


Application services
--------------------

These roles manage applications that provide services to other applications and
are not accessed directly by end users.

- :ref:`debops.ansible`
- :ref:`debops.apt_cacher_ng`
- :ref:`debops.controller` - install DebOps on other hosts
- :ref:`debops.debops_api`
- :ref:`debops.gitlab_runner`
- :ref:`debops.fcgiwrap`
- :ref:`debops.freeradius`
- :ref:`debops.gunicorn`
- :ref:`debops.keepalived`
- :ref:`debops.imapproxy`
- :ref:`debops.ldap`
- :ref:`debops.mcli`
- :ref:`debops.memcached`
- :ref:`debops.minio`
- :ref:`debops.mosquitto`
- :ref:`debops.nscd`
- :ref:`debops.rabbitmq_management`
- :ref:`debops.rabbitmq_server`
- :ref:`debops.salt`
- :ref:`debops.telegraf`
- :ref:`debops.tinyproxy`
- :ref:`debops.reprepro`
- ``debops.sks``
- ``debops-contrib.bitcoind``
- ``debops-contrib.x2go_server``


Backup
------

- :ref:`debops.backup2l`
- :ref:`debops.rsnapshot`
- ``debops.boxbackup``


Databases
---------

- :ref:`debops.elasticsearch`
- :ref:`debops.ldap`
- :ref:`debops.mariadb`
- :ref:`debops.mariadb_server`
- :ref:`debops.postgresql`
- :ref:`debops.postgresql_server`
- :ref:`debops.redis_server`
- :ref:`debops.redis_sentinel`
- :ref:`debops.slapd`
- :ref:`debops.influxdb`
- :ref:`debops.influxdb_server`
- ``debops.phpmyadmin``


Directory services
------------------

- :ref:`debops.ldap`
- :ref:`debops.nscd`
- :ref:`debops.nslcd`
- :ref:`debops.nsswitch`
- :ref:`debops.slapd`
- :ref:`debops.sssd`


Domain Name System
------------------

It's always DNS.

- :ref:`debops.avahi`
- :ref:`debops.dnsmasq`
- :ref:`debops.netbase`
- :ref:`debops.pdns`
- :ref:`debops.resolvconf`
- :ref:`debops.unbound`


Encryption
----------

- :ref:`debops.cryptsetup`
- :ref:`debops.dhparam`
- :ref:`debops.pki`


Filesystems
-----------

Ansible roles that manage filesystem-level services, or export filesystems to
other hosts.

- :ref:`debops.fhs`
- :ref:`debops.iscsi`
- :ref:`debops.lvm`
- :ref:`debops.mcli`
- :ref:`debops.minio`
- :ref:`debops.mount`
- :ref:`debops.nfs`
- :ref:`debops.nfs_server`
- :ref:`debops.persistent_paths`
- :ref:`debops.proc_hidepid`
- :ref:`debops.tftpd`
- :ref:`debops.tgt`
- ``debops.samba``
- ``debops-contrib.btrfs``
- ``debops-contrib.fuse``
- ``debops-contrib.snapshot_snapper``


Host provisioning
-----------------

- :ref:`debops.grub`
- :ref:`debops.ipxe`
- :ref:`debops.preseed`
- :ref:`debops.tftpd`
- ``debops-contrib.dropbear_initramfs``


Kernel
------

- :ref:`debops.kmod`
- :ref:`debops.sysctl`
- :ref:`debops.sysfs`


Logging
-------

- :ref:`debops.elasticsearch`
- :ref:`debops.filebeat`
- :ref:`debops.journald`
- :ref:`debops.kibana`
- :ref:`debops.logrotate`
- :ref:`debops.rsyslog`


Mail and SMS services
---------------------

- :ref:`debops.dovecot`
- :ref:`debops.etc_aliases`
- :ref:`debops.imapproxy`
- :ref:`debops.mailman`
- :ref:`debops.nullmailer`
- :ref:`debops.opendkim`
- :ref:`debops.postconf`
- :ref:`debops.postfix`
- :ref:`debops.postldap`
- :ref:`debops.postscreen`
- :ref:`debops.postwhite`
- :ref:`debops.roundcube`
- :ref:`debops.rspamd`
- :ref:`debops.saslauthd`
- ``debops.smstools``


Monitoring
----------

- :ref:`debops.dhcp_probe`
- :ref:`debops.icinga`
- :ref:`debops.icinga_db`
- :ref:`debops.icinga_web`
- :ref:`debops.librenms`
- :ref:`debops.monit`
- :ref:`debops.proc_hidepid`
- :ref:`debops.snmpd`
- :ref:`debops.telegraf`
- :ref:`debops.zabbix_agent`


Networking
----------

- :ref:`debops.avahi`
- :ref:`debops.dhcp_probe`
- :ref:`debops.dhcpd`
- :ref:`debops.dhcrelay`
- :ref:`debops.dnsmasq`
- :ref:`debops.freeradius`
- :ref:`debops.ifupdown`
- :ref:`debops.keepalived`
- :ref:`debops.lldpd`
- :ref:`debops.netbase`
- :ref:`debops.radvd`
- :ref:`debops.resolvconf`
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
- :ref:`debops.apt_mark`
- :ref:`debops.apt_preferences`
- :ref:`debops.apt_proxy`
- :ref:`debops.debops_legacy`
- :ref:`debops.extrepo`
- :ref:`debops.keyring`
- :ref:`debops.unattended_upgrades`
- :ref:`debops.reprepro`


Security
--------

- :ref:`debops.auth`
- :ref:`debops.authorized_keys`
- :ref:`debops.fail2ban`
- :ref:`debops.ferm`
- :ref:`debops.freeradius`
- :ref:`debops.keyring`
- :ref:`debops.libuser`
- :ref:`debops.pam_access`
- :ref:`debops.proc_hidepid`
- :ref:`debops.sshd`
- :ref:`debops.sudo`
- :ref:`debops.system_groups`
- :ref:`debops.system_users`
- :ref:`debops.tcpwrappers`
- ``debops-contrib.apparmor``
- ``debops-contrib.firejail``


System configuration
--------------------

- :ref:`debops.atd`
- :ref:`debops.console`
- :ref:`debops.cron`
- :ref:`debops.debops_legacy`
- :ref:`debops.environment`
- :ref:`debops.etc_services`
- :ref:`debops.etckeeper`
- :ref:`debops.ferm`
- :ref:`debops.fhs`
- :ref:`debops.keyring`
- :ref:`debops.ldap`
- :ref:`debops.locales`
- :ref:`debops.logrotate`
- :ref:`debops.machine`
- :ref:`debops.mount`
- :ref:`debops.netbase`
- :ref:`debops.nslcd`
- :ref:`debops.nsswitch`
- :ref:`debops.ntp`
- :ref:`debops.pam_access`
- :ref:`debops.resources`
- :ref:`debops.root_account`
- :ref:`debops.sssd`
- :ref:`debops.swapfile`
- :ref:`debops.sysctl`
- :ref:`debops.sysfs`
- :ref:`debops.sysnews`
- :ref:`debops.system_groups`
- :ref:`debops.system_users`
- :ref:`debops.tzdata`
- :ref:`debops.users`
- :ref:`debops.yadm`
- ``debops.gitusers``


Web services
------------

- :ref:`debops.apache`
- :ref:`debops.fcgiwrap`
- :ref:`debops.gunicorn`
- :ref:`debops.minio`
- :ref:`debops.nginx`
- :ref:`debops.nodejs`
- :ref:`debops.php`


Virtualization
--------------

- :ref:`debops.docker_gen`
- :ref:`debops.docker_registry`
- :ref:`debops.docker_server`
- :ref:`debops.libvirt`
- :ref:`debops.libvirtd`
- :ref:`debops.libvirtd_qemu`
- :ref:`debops.lxc`
- :ref:`debops.lxd`


Ansible internals
-----------------

These Ansible roles are used internally during playbook execution, or provide
additional functions to other roles.

- :ref:`debops.ansible_plugins`
- :ref:`debops.core`
- :ref:`debops.debops_fact`
- :ref:`debops.dpkg_cleanup`
- :ref:`debops.global_handlers`
- :ref:`debops.keyring`
- :ref:`debops.secret`
