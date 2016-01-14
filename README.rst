|debops_logo| DebOps playbooks
==============================

This repository contains all the playbooks used by `DebOps <http://debops.org>`_.

- `Here are a few services that are available`_
- `Overview of how playbooks work within DebOps`_
- `View a dependency graph`_
- `Status page`_

Here are a few services that are available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|Gratipay|_

**Fully loaded ready to go applications**

+---------+-----------+-----------+-----------+-----------+----------+----------+
| GitLab_ | GitLabCI_ | Etherpad_ | DokuWiki_ | ownCloud_ | phpIPAM_ | Mailman_ |
+---------+-----------+-----------+-----------+-----------+----------+----------+

**Databases**

+-------------+----------+--------+--------+------------+----------------+
| PostgreSQL_ | MariaDB_ | MySQL_ | Redis_ | Memcached_ | Elasticsearch_ |
+-------------+----------+--------+--------+------------+----------------+

**Programming languages**

+-------+---------+-------+---------+------+
| Ruby_ | Golang_ | Java_ | NodeJS_ | PHP_ |
+-------+---------+-------+---------+------+

**Web application deployment**

+--------+--------------+
| nginx_ | RubyOnRails_ |
+--------+--------------+

**Service monitoring and logging**

+-----------+--------+----------+
| LibreNMS_ | monit_ | rsyslog_ |
+-----------+--------+----------+

**Networking**

+----------+-------+--------+-------+----------+------+------+------+--------+
| dnsmasq_ | DHCP_ | Radvd_ | ferm_ | postfix_ | SMS_ | SSH_ | NFS_ | Samba_ |
+----------+-------+--------+-------+----------+------+------+------+--------+

**Virtualization**

+------+---------+---------+------+
| LXC_ | Docker_ | OpenVZ_ | KVM_ |
+------+---------+---------+------+

**Backup and encryption**

+-----------+------------+--------+------+---------------+
| Safekeep_ | BoxBackup_ | encFS_ | SKS_ | Monkeysphere_ |
+-----------+------------+--------+------+---------------+

**Security**

+------+----------+--------+-------------+--------+
| PKI_ | dhparam_ | slapd_ | cryptsetup_ | EncFS_ |
+------+----------+--------+-------------+--------+

Overview of how playbooks work within DebOps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There's a ``common.yml`` playbook which gets ran on every host except localhost.
This includes standard services like sshd and ferm. The full list can be
found `here <https://github.com/debops/debops-playbooks/blob/master/playbooks/common.yml>`_.

Additional plays are then ran based on what groups the host is in. For example if you wanted
to setup a Gitlab instance you would add a host to the ``[debops_gitlab]`` group
in your inventory.

That carries over for things like postgresql, ruby or any service for the most
part. You can also install roles as dependencies rather than use inventory groups.

The dependency approach makes sense in a lot of places, especially for setting
ports through ferm or perhaps installing a database for a role that demands that database.

You can view all of the services and plays
`here <https://github.com/debops/debops-playbooks/tree/master/playbooks>`_.

View a dependency graph
^^^^^^^^^^^^^^^^^^^^^^^

.. image:: http://debops.org/images/dependency-graph.png
   :alt: Dependency graph

Status page
^^^^^^^^^^^

If you want to keep tabs on each role's status then check out our
`status page <http://debops.org/status.html>`_.

.. |Gratipay| image:: https://img.shields.io/gratipay/drybjed.svg?style=flat
.. _Gratipay: https://www.gratipay.com/drybjed/
.. |debops_logo| image:: http://debops.org/images/debops-small.png

.. _Gitlab: https://github.com/debops/ansible-gitlab
.. _GitlabCI: https://github.com/debops/ansible-gitlab_ci
.. _Etherpad: https://github.com/debops/ansible-etherpad
.. _DokuWiki: https://github.com/debops/ansible-dokuwiki
.. _ownCloud: https://github.com/debops/ansible-ownCloud
.. _phpIPAM: https://github.com/debops/ansible-phpipam
.. _Mailman: https://github.com/debops/ansible-mailman

.. _PostgreSQL: https://github.com/debops/ansible-postgresql_server
.. _MariaDB: https://github.com/debops/ansible-mariadb_server
.. _MySQL: https://github.com/debops/ansible-mysql
.. _Redis: https://github.com/debops/ansible-redis
.. _Memcached: https://github.com/debops/ansible-memcached
.. _Elasticsearch: https://github.com/debops/ansible-elasticsearch

.. _Ruby: https://github.com/debops/ansible-ruby
.. _Golang: https://github.com/debops/ansible-golang
.. _Java: https://github.com/debops/ansible-java
.. _NodeJS: https://github.com/debops/ansible-nodejs
.. _PHP: https://github.com/debops/ansible-php5

.. _nginx: https://github.com/debops/ansible-nginx
.. _RubyOnRails: https://github.com/debops/ansible-rails_deploy

.. _LibreNMS: https://github.com/debops/ansible-librenms
.. _monit: https://github.com/debops/ansible-monit
.. _rsyslog: https://github.com/debops/ansible-rsyslog

.. _dnsmasq: https://github.com/debops/ansible-dnsmasq
.. _DHCP: https://github.com/debops/ansible-dhcpd
.. _Radvd: https://github.com/debops/ansible-radvd
.. _ferm: https://github.com/debops/ansible-ferm
.. _postfix: https://github.com/debops/ansible-postfix
.. _SMS: https://github.com/debops/ansible-smstools
.. _SSH: https://github.com/debops/ansible-sshd
.. _NFS: https://github.com/debops/ansible-nfs
.. _Samba: https://github.com/debops/ansible-samba

.. _LXC: https://github.com/debops/ansible-lxc
.. _Docker: https://github.com/debops/ansible-docker
.. _OpenVZ: https://github.com/debops/ansible-openvz
.. _KVM: https://github.com/debops/ansible-kvm

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
