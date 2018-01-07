Getting started
===============

.. contents::
   :local:

``debops.snmpd`` role will install ``snmpd`` package on Debian/Ubuntu hosts and
secure access to SNMP using random SNMPv3 username / password combination, as
well as firewall and TCP wrappers rules. Additionally, ``lldpd`` daemon will be
installed to provide `LLDP`_ support (this can be disabled by a variable).

.. _LLDP: https://en.wikipedia.org/wiki/Link_Layer_Discovery_Protocol

Example inventory
-----------------

To enable SNMP service on a DebOps-managed host, you need to add that host to
``[debops_snmpd]`` Ansible inventory group::

    [debops_snmpd]
    hostname

If you use separate host groups, better idea might be to create a parent group
and add your own host groups to it::

    [servers]
    host1
    host2

    [debops_snmpd:children]
    servers

Example playbook
----------------

Here's an example playbook which uses ``debops.snmpd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/snmpd.yml
   :language: yaml

Firewall, TCP wrappers access
-----------------------------

SNMP is primarly used over the network, but for security reasons access from
remote hosts is filtered by a firewall and TCP wrappers. To allow access to
SNMP from other hosts using ``debops.ferm`` and ``debops.tcpwrappers`` Ansible
roles, you need to add IP addresses or CIDR subnets which can access the
service to ``snmpd_*_allow`` lists::

  snmpd_allow: [ '192.0.2.0/24', '2001:db8::/48' ]

SNMPv3 authentication
---------------------

``debops.snmpd`` role will create three SNMPv3 user accounts with random
usernames and passwords, which will be stored on Ansible Controller in the
``secret/`` directory (see ``debops.secret`` role for more details).

Authentication uses SHA encryption, privacy mode uses AES encryption. The
generated accounts are:

- a global "admin" account, stored in ``secret/snmp/credentials/admin/``
  directory on Ansible Controller. Read-write, disabled after ``snmpd`` is
  configured. Will be the same on all servers in the cluster.

- a global "agent" account, stored in ``secret/snmp/credentials/agent/``
  directory on Ansible Controller. Read-only, meant to be used to access the
  SNMP service using network management software. Will be the same on all
  servers in the cluster.

- a "local" account, stored in ``/etc/snmp/snmp.local.conf`` and
  ``/etc/ansible/facts.d/snmpd.fact`` files on remote hosts. Unique to
  a particular host, read only. Allows access from the host to itself from the
  ``root`` account, can be used to grant access to a particular host data to
  other users or services.

