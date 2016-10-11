Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

An Elasticsearch cluster can be built from different nodes with different
capabilities. The following Ansible inventory groups can be used:

``debops_service_elasticsearch_master``
  General purpose node which can act as master but also persistently stores
  index data.

``debops_service_elasticsearch_workhorse``
  Elasticsearch worker nodes which persistenlty store index data but shouldn't
  become master nodes.

``debops_service_elasticsearch_coordinator``
  Elasticsearch nodes which can act as master but shouldn't store persistent
  index data.

``debops_service_elasticsearch_loadbalancer``
  Elasticsearch nodes which shouldn't become master and shouldn't store
  persistent data but act as load balancer or traffic aggregators.

If you only have one node or only start using Elasticsearch you should add
your host to the ``[debops_service_elasticsearch_master]`` Ansible inventory
group:

.. code-block:: none

    [debops_service_elasticsearch_master]
    hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.elasticsearch`` role:

.. literalinclude:: playbooks/elasticsearch.yml
   :language: yaml
