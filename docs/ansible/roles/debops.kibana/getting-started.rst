Getting started
===============

.. contents::
   :local:


Upstream package is used by default
-----------------------------------

The Debian and Ubuntu archives contain the ``elasticsearch`` packages, however
they are very old releases (1.x). The `security support for the package in Debian has been discontinued <https://lists.debian.org/debian-security-announce/2015/msg00290.html>`_
due to issues with upstream security policy (`Debian Bug #803713 <https://bugs.debian.org/803713>`_).
Debian Developers suggest that `in production environments the upstream version should be used <https://bugs.debian.org/829078>`_
to provide adequate security updates.

Due to the above reasons, the role is focused on the upstream Kibana release
only (5.x+) to keep compatibility with upstream Elasticsearch. The package
installation itself is handled by the ``debops.elastic_co`` Ansible role which
also manages upstream APT repository configuration.


Kibana is insecure by default
-----------------------------

The Kibana dashboard relies on Elasticsearch to ensure secure communication
between cluster nodes. The default configuration expects an Elasticsearch
instance installed on the same host, preferably in a "load balancer" mode, that
is with no master possibility, no data or ingest functions enabled on the node.

Kibana by default does not include any authentication or ACL support; however
the role by default does not configure any access restrictions. If you want to
have a simple security solution, you can use ``kibana__webserver_*`` variables
to configure HTTP Basic Auth in the :command:`nginx` frontend. Keep in mind
that once a user is authenticated using this method, he/she has full access to
the Elasticsearch cluster.

You can install additional plugins that provide encrypted connections,
authentication, authorization and access control:

- `X-Pack <https://www.elastic.co/products/x-pack>`_, an Elastic
  commercial plugin with free trial period. Supports encryption,
  authentication, access control, integrates with Elasticsearch and Logstash.
  Since the plugin is developed by the same team, its releases are in parallel
  with Kibana.

- `Search Guard <http://floragunn.com/searchguard/>`_, an open source third
  party plugin with commercial support. Has features comparable with X-Pack,
  with more basic features like HTTP and transport encryption, basic
  authentication and access control available free of charge.


Use as a role dependency
------------------------

The Kibana main configuration file
`does not support an include statement or conf.d directory <https://github.com/elastic/elasticsearch/issues/11362>`_.
To mitigate that and allow multiple Kibana configuration sources from other
Ansible roles, the ``debops.kibana`` role supports operation as a dependent
role. This functionality can be used by other Ansible roles to better manage
Kibana plugins or extend the configuration without the need to implement the
entire role again and with preserved idempotency.

See the :ref:`kibana__ref_dependency` for more details.


Example inventory
-----------------

To deploy Kibana, you can add the host to the
``[debops_service_kibana]`` Ansible inventory group. By default Kibana expects
an Elasticsearch instance on the same host to leverage the cluster load
balancing. To install an ES node in a load balancer configuration, include the
host in the ``[debops_service_elasticsearch_lb]`` inventory group:

.. code-block:: none

   [debops_service_kibana]
   hostname

   [debops_service_elasticsearch_lb]
   hostname

See the documentation of the ``debops.elasticsearch`` role about different
Ansible inventory group types and their usage.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.kibana`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/kibana.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::kibana``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::kibana:config``
  Generate the Kibana configuration taking into account different configuration
  sources.
