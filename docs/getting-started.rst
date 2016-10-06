Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


Example inventory
-----------------

Elasticsearch consists of various components. 
To setup Elasticsearch on a given remote host, it needs to be added to
``[debops_service_elasticsearch]`` Ansible inventory group:

.. code-block:: none

    [debops_service_elasticsearch]
    hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.elasticsearch`` role:

.. literalinclude:: playbooks/elasticsearch.yml
   :language: yaml
