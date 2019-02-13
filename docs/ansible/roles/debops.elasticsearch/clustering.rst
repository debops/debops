.. _elasticsearch__ref_clustering:

Elasticsearch clustering
========================

The Elasticsearch service can be deployed either on a single host in
a "standalone" mode, or in a cluster of multiple hosts. The cluster mode will be enabled automatically after a few important variables and inventory groups are configured.

.. contents::
   :local:


Standalone mode vs cluster mode
-------------------------------

In a standalone mode, the Elasticsearch service will not try to talk with any
other Elasticsearch nodes. Service will be usable over ``localhost``
connection. This mode is good for prototyping, testing and development
environments, however it's not very resilient.

In a cluster mode, multiple Elasticsearch nodes talk to each other in
a configured network subnet, over TCP. Elasticsearch
clients communicate with the cluster over HTTP REST interface, usually via
a dedicated host with Kibana and/or Logstash as an intermediary.


Playbook execution
------------------

When multiple Elasticsearch hosts are managed as a cluster, any changes in the
cluster configuration should be implemented on all hosts in the cluster at the
same time to avoid issues with split-brain or quorum. The role uses inventory
groups to compute some specific values for all hosts in the cluster, however
using the ``--limit`` parameter of the :command:`ansible-playbook` command will
only configure those values on a subset of hosts. Remember to always keep the
whole cluster configuration synchronized by running the Elasticsearch playbook
on all hosts included in the cluster (without the ``--limit`` parameter).


Ansible inventory groups
------------------------

The ``debops.elasticsearch`` role uses a set of Ansible inventory groups to
detect the Elasticsearch node type and change the configuration accordingly.

The main inventory group is ``[debops_service_elasticsearch]``. Hosts in this
group are configured to behave in the same way - all of them are eligible to be
a master host, all of them can hold data, and all of them can use an ingest
pipeline to process the input. This group is useful in small clusters,
typically <10 hosts in total.

In larger clusters, the system administrator may want to separate the cluster
hosts into separate node types. Each Ansible inventory group enables a separate
feature, and hosts can be in multiple groups at once to mix and match the
desired features:

``[debops_service_elasticsearch_master]``
  Hosts in this Ansible inventory group are eligible to become masters.

``[debops_service_elasticsearch_data]``
  Hosts in this Ansible inventory group can hold data shards.

``[debops_service_elasticsearch_ingest]``
  Hosts in this Ansible inventory group can process incoming data via an ingest
  pipeline.

``[debops_service_elasticsearch_lb]``
  Hosts in this Ansible inventory group do not have any features explicitly
  enabled, and act as load balancers and coordinators within the cluster.

You can check the `Elasticsearch node documentation <https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-node.html>`_
for more details about node features.

The inventory groups and their corresponding node functions are defined using
default variables. The role uses Ansible inventory groups to automatically
determine the list of hosts which will be used for discovery, as well as the number
of eligible master hosts, therefore direct changes to the node function
variables should be done with care.


Unicast host discovery, number of master hosts
----------------------------------------------

The role automatically manages the list of hosts which should be contacted for
initial host discovery and number of master-eligible nodes based on the Ansible
inventory group membership.

If the ``[debops_service_elasticsearch_master]`` group is not used, all of the
hosts in the ``[debops_service_elasticsearch]`` inventory group will be added
to the unicast discovery list, and all of them will be eligible to become
masters.

When hosts are included in the ``[debops_service_elasticsearch_master]``
inventory group, only hosts in this group will be able to become masters, and
only hosts in this group will be used for initial unicast discovery. Remember
to always include an odd number of master-eligible hosts to achieve quorum
majority within the cluster.


Firewall configuration
----------------------

The role supports a firewall managed by the :ref:`debops.ferm` Ansible role. When the
firewall is enabled, Elasticsearch will be configured to listen to connections
on private IP addresses defined on the host along with the ``localhost``; if
the firewall is not detected or disabled, Elasticsearch will listen only on the
``localhost`` interface by default.

To enable cluster mode, you need to define at least one IP address or a CIDR
subnet in the :envvar:`elasticsearch__allow_tcp` list. Make sure to only allow
access from trusted hosts!

There's also a separate :envvar:`elasticsearch__allow_http` variable, but you
don't need to enable it unless you need a direct access to the Elasticsearch
HTTP REST interface from remote hosts. Kibana and Logstash installed on the
same host as an Elasticsearch service should be able to talk to it over
``localhost`` with no issues.
