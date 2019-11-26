.. _slapd__ref_syncrepl_multi_master:

Guide: N-Way Multi-Master replication
=====================================

The `N-Way Multi-Master replication`__ can be used to create and manage
multiple master LDAP directory servers that share the data between them. This
configuration can provide better LDAP directory service availability via host
and database redundancy, failover capability and easy sharing of the LDAP
database contents across multiple sites.

.. __: https://www.openldap.org/doc/admin24/replication.html#N-Way%20Multi-Master%20replication

.. contents::
   :local:


Introduction
------------

There are arguments for and against this setup (see the OpenLDAP documentation
linked above). N-Way Multi-Master replication is a good solution for the core
infrastructure to provide redundancy and failover; it might be a wrong approach
for providing LDAP directory services "closer" to the end-users, for this you
might want to look into `other OpenLDAP replication topologies`__ (check out
the `Zytrax guide about OpenLDAP replication`__ as well).

.. __: https://www.openldap.org/doc/admin24/replication.html
.. __: http://www.zytrax.com/books/ldap/ch7/

This guide shows how to implement N-Way Multi-Master replication of the LDAP
directory using DebOps. You might want to check `example configuration`__ in
the OpenLDAP documentation for comparsion. There's also `Zytrax guide`__
available that also has a Multi-Master replication example.

.. __: https://www.openldap.org/doc/admin24/replication.html#N-Way%20Multi-Master
.. __: http://www.zytrax.com/books/ldap/ch7/#ol-syncrepl-mm


Requirements
------------

- At least 2 Debian hosts configured by DebOps/Ansible, there can be more hosts
  included in the cluster.
- All hosts have proper time synchronization using NTP.
- All hosts can reach each other via DNS hostnames and the firewall + TCP
  Wrappers access has been allowed using the ``slapd__*_allow`` variables.


DNS configuration
-----------------

For flexibility, the LDAP directory cluster will be reachable to the clients
using ``CNAME`` and ``SRV`` records. Here's an example :man:`dnsmasq(8)`
configuration for 3 OpenLDAP cluster hosts and 1 OpenLDAP test host used for
development:

.. code-block:: ini

   host-record = slapd-server1.example.org,192.0.2.1
   host-record = slapd-server2.example.org,192.0.2.2
   host-record = slapd-server3.example.org,192.0.2.3

   host-record = slapd-tests.example.org,192.0.2.4

   cname = ldap1.example.org,slapd-server1.example.org
   cname = ldap2.example.org,slapd-server2.example.org
   cname = ldap3.example.org,slapd-server3.example.org

   srv-host = _ldap._tcp.example.org,ldap1.example.org,389,10,0
   srv-host = _ldap._tcp.example.org,ldap2.example.org,389,20,0
   srv-host = _ldap._tcp.example.org,ldap3.example.org,389,30,0

   cname = ldap.example.org,slapd-server1.example.org

   cname = ldap-test.example.org,slapd-tests.example.org

The LDAP clients that use the ``SRV`` records will by default connect to the
``ldap1.example.org`` server, therefore you might expect increased traffic to
it. Additional OpenLDAP servers will be used as fallback when
``ldap1.example.org`` server is unreachable. With this setup it should be very
easy to replace the OpenLDAP servers with new ones on the DNS level, without
the need to reconfigure LDAP clients everywhere.

Part of the cluster that is used for testing an development should be
configured to connect directly to the ``ldap-test.example.org`` server and not
use the ``SRV`` records.

Keep in mind that in the replicated ``cn=config`` configuration (see below) you
should use the real server hostnames, and not the ``CNAME`` records, to avoid
possible issues when cluster nodes are replaced.


Ansible inventory configuration
-------------------------------

Each OpenLDAP database has its own replication configuration. For maximum
consistency, the ``cn=config`` database should also be replicated, which means
that each cluster node has to be able to work using the same configuration
options.

In the Ansible inventory, you should create an Ansible inventory group for the
OpenLDAP cluster, let's call it ``[slapd_masters_cluster1]``, just in case that
in the future there will be multiple OpenLDAP clusters. You could also create
a separate OpenLDAP server not connected to the main cluster for development
and testing.

.. code-block:: none

   [debops_all_hosts]
   slapd-server1    ansible_host=slapd-server1.example.org
   slapd-server2    ansible_host=slapd-server2.example.org
   slapd-server3    ansible_host=slapd-server3.example.org

   slapd-tests      ansible_host=slapd-tests.example.org

   [debops_service_slapd]
   slapd-server1
   slapd-server2
   slapd-server3

   slapd-tests

   [slapd_masters_cluster1]
   slapd-server1
   slapd-server2
   slapd-server3


OpenLDAP configuration tasks
----------------------------

The specific :ref:`OpenLDAP tasks <slapd__ref_tasks>` that are used to
configure the replication between the cluster nodes will be stored in the
:file:`ansible/inventory/group_vars/slapd_masters_cluster1/slapd.yml` inventory
file.

The example OpenLDAP configuration for 3 master nodes, each replicating the
``cn=config`` database and the main database:

.. literalinclude:: examples/multi-master-replication.yml
   :language: yaml

The above configuration is available as a convenience in a separate
:file:`examples/multi-master-replication.yml` file in the :ref:`debops.slapd`
role documentation stored in the DebOps monorepo.

Configuration notes
~~~~~~~~~~~~~~~~~~~

- The support for the ``X-ORDERED`` LDAP extension via the ``ordered``
  parameter is not used here, because the tasks contain attributes not
  compatible with ``X-ORDERED`` syntax (``olcMirrorMode``) which have to be
  activated at the same time.

- The ``olcServerID`` values and ``rid=`` values are unrelated to each other.
  Each OpenLDAP server needs an unique ServerID.

- The ``rid=`` values need to be numbers from ``000`` to ``999``. A suggested
  way of using them is to use the first digit as a synchronization group (``0``
  for multi-master nodes, ``1`` for normal Sync Replication, etc.), second
  digit as the database number (``0`` for the ``cn=config`` database, ``1`` for
  the main database, and so on), and third digit for the OpenLDAP server
  instance, starting from ``0``. You might want to design your own scheme of
  course.

- The Sync Replication security depends on X.509 certificates and PKI. The
  :ref:`debops.slapd` role depends on the PKI environment managed by the
  :ref:`debops.pki` Ansible role to manage the certificates. Because the
  configuration will be shared between all of the masters in the cluster, they
  should use a similar configuration, including the name of the PKI realm used
  by the role.


Deployment
----------

After the configuration is in the Ansible inventory, you should apply it on all
OpenLDAP servers in the cluster at once:

.. code-block:: console

   debops service/slapd -l slapd_masters_cluster1 --diff

When the deployment is complete, OpenLDAP configuration should be defined on
the group level instead of on the individual host level in the inventory. The
OpenLDAP servers will synchronize the configuration between the nodes in both
cases, but it might be confusing if you see configuration defined for one host
suddenly "show up" on other nodes in the cluster.

Some of the OpenLDAP configuration options, for example module loading and
overlay setup should be done on only one node of the cluster at a time; the
changes will be propagated automatically. Otherwise you will notice that during
the Ansible run one more nodes have finished with an error. This happens when
the role tries to enable a functionality on multiple OpenLDAP cluster nodes at
once, and the second time gets rejected by the cluster.

Remember that only the OpenLDAP configuration is synchronized automatically.
Other Ansible roles involved in the :ref:`debops.slapd` configuration, for
example firewall of TCP Wrappers configuration,  still need to be applied on
all hosts in the OpenLDAP cluster.
