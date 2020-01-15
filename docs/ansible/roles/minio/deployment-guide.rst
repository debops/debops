.. _minio__ref_deployment_guide:

MinIO deployment guide
======================

MinIO can be deployed in different ways depending on the desired configuration.
You should refer to the `MinIO documentation`__ for various deployment
examples. This page focuses on explaining how to `deploy MinIO in multi-tenant
environment`__ using the :ref:`debops.minio` Ansible role to provide more
complex examples of the role usage.

.. __: https://docs.min.io/
.. __: https://docs.min.io/docs/multi-tenant-minio-deployment-guide.html

.. warning:: Once deployed, the structure of the MinIO cluster cannot be
   changed (`new disks/hosts cannot be added/removed from the cluster`__). It's
   best to prepare the desired configuration in a development environment
   before deploying it in production.

   .. __: https://github.com/minio/minio/issues/4364

.. contents::
   :local:


PKI infrastructure
------------------

MinIO supports encrypted connections using TLS and X.509 certificates - when
this mode is enabled, unencrypted HTTP connections are disabled, therefore
communication with upstream MinIO services through the :command:`nginx` proxy
has to be done over HTTPS. The TLS protocol also enforces checking the
``Host:`` HTTP header against the currently enabled X.509 certificates - any
connections to hosts or IP addresses not in the X.509 certificates will be
denied.

The :ref:`debops.minio` role uses the PKI infrastructure maintained by the
:ref:`debops.pki` role when available. The default PKI deployment configures an
internal Certificate Authority which is trusted by all hosts in the cluster; the
host certificates contain wildcard addresses for the domain part as well as
host subdomains, which simplifies the internal certificate management. However,
if you plan to use public X.509 certificates for MinIO services directly, you
need to ensure that the certificates use the correct FQDNs for each host in the
cluster. The :ref:`debops.minio` role currently does not support using IP
addresses for connections, this feature can be implemented if there's a demand
for it.

Since connections from the outside to the MinIO cluster via the
:command:`nginx` proxy can be handled by a separate set of certificates, use of
the internal CA and the ``domain`` PKI realm for MinIO service is currently
recommended.


Single tenant, multiple nodes
-----------------------------

The default ``main`` MinIO instance is configured for a single tenant on
multiple, separate hosts with its access and secret keys stored in the
:file:`secret/minio/distributed/main/` files on the Ansible Controller (see
:ref:`debops.secret` role documentation for details). This configuration allows
easy scaling of storage by setting up additional hosts with MinIO service
installed on each one. The access and secret keys will be the same, therefore
your application(s) can use the same credentials to access the storage on
different nodes. An example inventory with 2 MinIO hosts:

.. code-block:: none

   # ansible/inventory/hosts

   # Configure Ansible inventory groups
   [debops_all_hosts]
   server1    ansible_host=server1.example.org
   server2    ansible_host=server2.example.org

   [debops_service_minio]
   server1
   server2

The MinIO instances will be reachable directly via these addresses:

- ``https://server1.example.org:9000/``
- ``https://server2.example.org:9000/``

The :command:`nginx` HTTP proxy configured by :ref:`debops.minio` role will
publish the MinIO instances on these addresses:

- ``https://server1.example.org/``
- ``https://server2.example.org/``

You can combine separate MinIO instances in a `federated mode`__ to make host
lookups via DNS easier, however this configuration is currently out of scope
for the :ref:`debops.minio` role.

.. __: https://docs.min.io/docs/minio-federation-quickstart-guide.html


Single tenant, single node
--------------------------

If you want to configure separate tenants on each MinIO host, for example by
separating tenants using LXC containers and frontend HTTP proxy, you can easily
change the ``main`` MinIO instance to standalone configuration by setting in
the inventory:

.. code-block:: none

   # ansible/inventory/hosts

   # Configure Ansible inventory groups
   [debops_all_hosts]
   tenant1    ansible_host=tenant1.example.org
   tenant2    ansible_host=tenant2.example.org
   tenant3    ansible_host=tenant3.example.org

   [debops_service_minio]
   tenant1
   tenant2
   tenant3

.. code-block:: yaml

   # ansible/inventory/group_vars/all/minio.yml

   # Override configuration for 'main' instance
   minio__instances:
     - name: 'main'
       standalone: True

With this configuration, each MinIO ``main`` instance on a separate host gets
its own set of access and secret keys stored in the
:file:`secret/minio/standalone/<host>/main/` directory on the Ansible
Controller.

The MinIO instances will be reachable directly via these addresses:

- ``https://tenant1.example.org:9000/``
- ``https://tenant2.example.org:9000/``
- ``https://tenant3.example.org:9000/``

The :command:`nginx` HTTP proxy configured by :ref:`debops.minio` role will
publish the MinIO instances on these addresses:

- ``https://tenant1.example.org/``
- ``https://tenant2.example.org/``
- ``https://tenant3.example.org/``

The DNS records and the X.509 certificates may contain wildcard addresses
(``*.tenant1.example.org``, etc.) to allow access to buckets via subdomains in
addition to access via subdirectories; for example
``https://bucket.tenant1.example.org`` will redirect to
``https://tenant1.example.org/bucket/``.


Standalone deployment
---------------------

In a `standalone deployment example`__, we will configure MinIO with three
tenants on a single MinIO host, once with a single disk drive, and once with
multiple disk drives. In this example, the ``main`` MinIO cluster will be
removed for consistency.

.. __: https://docs.min.io/docs/multi-tenant-minio-deployment-guide.html#standalone-deployment

Each MinIO tenant instance will be accessible over a separate TCP port. The
:command:`nginx` proxy configured by the :ref:`debops.minio` role will also
allow connections to each MinIO instance based on its ``name`` parameter as
a subdomain of the main DNS domain of the host. For that to work reliably,
X.509 certificates used by the :ref:`debops.nginx` role need to include the
relevant FQDN addresses.

The host configuration in the Ansible inventory:

.. code-block:: none

   # ansible/inventory/hosts

   # Configure Ansible inventory groups
   [debops_all_hosts]
   server    ansible_host=server.example.org

   [debops_service_minio]
   server

The MinIO instances will be reachable directly via these addresses:

- ``https://server.example.org:9001/``
- ``https://server.example.org:9002/``
- ``https://server.example.org:9003/``

The :command:`nginx` HTTP proxy configured by :ref:`debops.minio` role will
publish the MinIO instances on these addresses:

- ``https://tenant1.example.org/``
- ``https://tenant2.example.org/``
- ``https://tenant3.example.org/``

Note that the proxied URLs are based on the MinIO instance names instead of the
host names. The DNS configuration which directs the above FQDNs to the
``server.example.org`` host has to be performed separately.

Multiple tenants on a single drive
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this set up there's a single host with large disk drive mounted at
:file:`/data` mount point (mounting can be configured by the
:ref:`debops.mount` Ansible role). Since the default is to configure the MinIO
instance volumes at :file:`/srv/minio/` directory, we override that using the
:envvar:`minio__volumes_dir` variable. The role will configure each MinIO
instance to use a subdirectory in the :file:`/data` directory.

.. code-block:: yaml

   # ansible/inventory/host_vars/server/minio.yml

   # Override default MinIO volumes path
   minio__volumes_dir: '/data'

   # Ensure that data directory is accessible by the 'minio' UNIX account
   minio__host_volumes:
     - '/data'

   # Configure MinIO instances
   minio__host_instances:

     - name: 'main'
       state: 'absent'

     - name: 'tenant1'
       port: 9001

     - name: 'tenant2'
       port: 9002

     - name: 'tenant3'
       port: 9003

Multiple tenants on multiple drives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this case the storage server has 4 disk drives mounted at
:file:`/disk\\{1,4\\}/` directories. Here we have to specify each volume directly
for each tenant, so that the data is distributed among the disk drives.

.. code-block:: yaml

   # ansible/inventory/host_vars/server/minio.yml

   # Ensure that data directories are accessible by the 'minio' UNIX account
   minio__host_volumes:
     - '/disk1/data'
     - '/disk2/data'
     - '/disk3/data'
     - '/disk4/data'

   # Configure MinIO instances
   minio__host_instances:

     - name: 'main'
       state: 'absent'

     - name: 'tenant1'
       port: 9001
       volumes:
         - '/disk1/data/tenant1'
         - '/disk2/data/tenant1'
         - '/disk3/data/tenant1'
         - '/disk4/data/tenant1'

     - name: 'tenant2'
       port: 9002
       volumes:
         - '/disk1/data/tenant2'
         - '/disk2/data/tenant2'
         - '/disk3/data/tenant2'
         - '/disk4/data/tenant2'

     - name: 'tenant3'
       port: 9003
       volumes:
         - '/disk1/data/tenant3'
         - '/disk2/data/tenant3'
         - '/disk3/data/tenant3'
         - '/disk4/data/tenant3'


Distributed deployment
----------------------

The `distributed MinIO deployment`__ uses multiple hosts to distribute the data
across a number of devices to improve resiliency. The minimum amount of hosts
required by MinIO is 4, maximum is 32.

.. __: https://docs.min.io/docs/multi-tenant-minio-deployment-guide.html#distributed-deployment

In this example, we will use 4 hosts with single disk each, mounted at the
:file:`/data` directory. The connection between MinIO instances will be done
over TLS, connecting to the TCP ports directly. The :command:`nginx` proxies on
each host will be configured to direct the traffic to the local MinIO instance,
in which case the ``tenant\\{1,4\\}.example.org`` DNS records should point to
all ``server\\{1,4\\}.example.org`` hosts in a round-robin fashion.

An example Ansible inventory (note that the configuration is set at the
``[minio_cluster1]`` group level, not the host level):

.. code-block:: none

   # ansible/inventory/hosts

   # Configure Ansible inventory groups
   [debops_all_hosts]
   server1    ansible_host=server1.example.org
   server2    ansible_host=server2.example.org
   server3    ansible_host=server3.example.org
   server4    ansible_host=server4.example.org

   [minio_cluster1]
   server1
   server2
   server3
   server4

   [debops_service_minio:children]
   minio_cluster1

The MinIO ``tenant1`` instance will be reachable directly via these addresses:

- ``https://server1.example.org:9001/``
- ``https://server2.example.org:9001/``
- ``https://server2.example.org:9001/``
- ``https://server4.example.org:9001/``

You can reach other MinIO instances in the same way by changing the destination
TCP port.

The :command:`nginx` HTTP proxy configured by :ref:`debops.minio` role will
publish the MinIO instances on these addresses:

- ``https://tenant1.example.org/``
- ``https://tenant2.example.org/``
- ``https://tenant3.example.org/``

The DNS configuration which directs the above FQDNs to the underlying hosts has
to be performed separately. You should use a round-robin DNS records, where
each ``tenantX.example.org`` record points to all servers in the cluster.

The configuration for the entire cluster is defined on the Ansible inventory
group level, in this case ``[minio_cluster1]`` group. There can be multiple
clusters defined in the Ansible inventory, just make sure that the
MinIO-related variables don't overlap between groups.

.. code-block:: yaml

   # ansible/inventory/group_vars/minio_cluster1/minio.yml

   # Ensure that data directory is accessible by the 'minio' UNIX account
   minio__group_volumes:
     - '/data'

   # Configure MinIO instances
   minio__group_instances:

     - name: 'main'
       state: 'absent'

     - name: 'tenant1'
       port: 9001
       fqdn: 'tenant1.example.org'
       volumes:
         - 'https://server1.example.org:9001/data/tenant1'
         - 'https://server2.example.org:9001/data/tenant1'
         - 'https://server3.example.org:9001/data/tenant1'
         - 'https://server4.example.org:9001/data/tenant1'

     - name: 'tenant2'
       port: 9002
       fqdn: 'tenant2.example.org'
       volumes:
         - 'https://server1.example.org:9002/data/tenant2'
         - 'https://server2.example.org:9002/data/tenant2'
         - 'https://server3.example.org:9002/data/tenant2'
         - 'https://server4.example.org:9002/data/tenant2'

     - name: 'tenant3'
       port: 9003
       fqdn: 'tenant3.example.org'
       volumes:
         - 'https://server1.example.org:9003/data/tenant3'
         - 'https://server2.example.org:9003/data/tenant3'
         - 'https://server3.example.org:9003/data/tenant3'
         - 'https://server4.example.org:9003/data/tenant3'
