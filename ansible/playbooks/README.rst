|debops_logo| DebOps playbooks
==============================

|CII Best Practices|

.. |CII Best Practices| image:: https://bestpractices.coreinfrastructure.org/projects/237/badge
   :target: https://bestpractices.coreinfrastructure.org/projects/237

This repository contains all the playbooks used by `DebOps <https://debops.org>`_.

- `Here are a few services that are available`_
- `Overview of how playbooks work within DebOps`_
- `View a dependency graph`_
- `Status page`_

Here are a few services that are available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Fully loaded ready to go applications**

+---------+-----------+-----------+-----------+-----------+----------+----------+
| GitLab_ | GitLabCI_ | Etherpad_ | DokuWiki_ | ownCloud_ | phpIPAM_ | Mailman_ |
+---------+-----------+-----------+-----------+-----------+----------+----------+

**Databases**

+-------------+----------+--------+------------+----------------+
| PostgreSQL_ | MariaDB_ | Redis_ | Memcached_ | Elasticsearch_ |
+-------------+----------+--------+------------+----------------+

**Programming languages**

+-------+---------+-------+---------+------+
| Ruby_ | Golang_ | Java_ | NodeJS_ | PHP_ |
+-------+---------+-------+---------+------+

**Web application deployment**

+--------+---------+--------------+
| nginx_ | Apache_ | RubyOnRails_ |
+--------+---------+--------------+

**Service monitoring and logging**

+-----------+--------+----------+
| LibreNMS_ | monit_ | rsyslog_ |
+-----------+--------+----------+

**Networking**

+----------+-------+--------+-------+----------+------+------+------+--------+-------+
| dnsmasq_ | DHCP_ | Radvd_ | ferm_ | postfix_ | SMS_ | SSH_ | NFS_ | Samba_ | Tinc_ |
+----------+-------+--------+-------+----------+------+------+------+--------+-------+

**Virtualization**

+------+---------+----------+
| LXC_ | Docker_ | libvirt_ |
+------+---------+----------+

**Backup and encryption**

+-----------+------------+--------+-------------+------+---------------+
| Safekeep_ | BoxBackup_ | encFS_ | cryptsetup_ | SKS_ | Monkeysphere_ |
+-----------+------------+--------+-------------+------+---------------+

**Security**

+------+----------+--------+
| PKI_ | dhparam_ | slapd_ |
+------+----------+--------+

Overview of how playbooks work within DebOps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There's a ``common.yml`` playbook which gets ran on every host except localhost.
This includes standard services like ``sshd`` and ferm. The full list can be
found `here <https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml>`__.

Additional plays are then ran based on what groups the host is in. For example if you wanted
to setup a Gitlab instance you would add a host to the ``[debops_service_gitlab]`` group
in your inventory.

That carries over for things like postgresql, ruby or any service for the most
part. You can also install roles as dependencies rather than use inventory groups.

The dependency approach makes sense in a lot of places, especially for setting
ports through ferm or perhaps installing a database for a role that demands that database.

You can view all of the services and plays
`here <https://github.com/debops/debops-playbooks/tree/master/playbooks>`_.

View a dependency graph
^^^^^^^^^^^^^^^^^^^^^^^

.. image:: https://debops.org/images/dependency-graph.png
   :alt: Dependency graph
   
The dependency graph was generated using: `ansigenome <https://github.com/nickjj/ansigenome>`__.


Status page
^^^^^^^^^^^

If you want to keep tabs on each role's status then check out our
`status page <https://debops.org/status.html>`_.

.. |debops_logo| image:: https://debops.org/images/debops-small.png

.. _Gitlab: https://github.com/debops/ansible-gitlab
.. _GitlabCI: https://github.com/debops/ansible-gitlab_ci
.. _Etherpad: https://github.com/debops/ansible-etherpad
.. _DokuWiki: https://github.com/debops/ansible-dokuwiki
.. _ownCloud: https://github.com/debops/ansible-ownCloud
.. _phpIPAM: https://github.com/debops/ansible-phpipam
.. _Mailman: https://github.com/debops/ansible-mailman

.. _PostgreSQL: https://github.com/debops/ansible-postgresql_server
.. _MariaDB: https://github.com/debops/ansible-mariadb_server
.. _Redis: https://github.com/debops/ansible-redis
.. _Memcached: https://github.com/debops/ansible-memcached
.. _Elasticsearch: https://github.com/debops/ansible-elasticsearch

.. _Ruby: https://github.com/debops/ansible-ruby
.. _Golang: https://github.com/debops/ansible-golang
.. _Java: https://github.com/debops/ansible-java
.. _NodeJS: https://github.com/debops/ansible-nodejs
.. _PHP: https://github.com/debops/ansible-php

.. _nginx: https://github.com/debops/ansible-nginx
.. _Apache: https://github.com/debops/ansible-apache
.. _RubyOnRails: https://github.com/debops/ansible-rails_deploy

.. _LibreNMS: https://github.com/debops/ansible-librenms
.. _monit: https://github.com/debops/ansible-monit
.. _rsyslog: https://github.com/debops/ansible-rsyslog

.. _dnsmasq: https://github.com/debops/ansible-dnsmasq
.. _DHCP: https://github.com/debops/ansible-dhcpd
.. _Tinc: https://github.com/debops/ansible-tinc
.. _Radvd: https://github.com/debops/ansible-radvd
.. _ferm: https://github.com/debops/ansible-ferm
.. _postfix: https://github.com/debops/ansible-postfix
.. _SMS: https://github.com/debops/ansible-smstools
.. _SSH: https://github.com/debops/ansible-sshd
.. _NFS: https://github.com/debops/ansible-nfs
.. _Samba: https://github.com/debops/ansible-samba

.. _LXC: https://github.com/debops/ansible-lxc
.. _Docker: https://github.com/debops/ansible-docker
.. _libvirt: https://github.com/debops/ansible-libvirt

.. _Safekeep: https://github.com/debops/ansible-safekeep
.. _BoxBackup: https://github.com/debops/ansible-boxbackup
.. _encFS: https://github.com/debops/ansible-encfs
.. _SKS: https://github.com/debops/ansible-sks
.. _Monkeysphere: https://github.com/debops/ansible-monkeysphere

.. _PKI: https://github.com/debops/ansible-pki
.. _dhparam: https://github.com/debops/ansible-dhparam
.. _slapd: https://github.com/debops/ansible-slapd
.. _cryptsetup: https://github.com/debops-contrib/ansible-cryptsetup
.. _EncFS: https://github.com/debops/ansible-encfs
