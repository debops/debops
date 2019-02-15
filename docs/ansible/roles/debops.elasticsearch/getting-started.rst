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

Due to the above reasons, the role is focused on the upstream Elasticsearch
release only (5.x+). The package installation itself is handled by the
``debops.elastic_co`` Ansible role which also manages upstream APT repository
configuration.


Elasticsearch is insecure by default
------------------------------------

The Elasticsearch service in the default configuration supports only plaintext
connections between the cluster nodes themselves, and between the cluster and
clients. There's no client authentication or authorization policies as well.
Due to that you should take care to not expose your Elasticsearch cluster to
the outside world without proper encryption and authentication.

You can install additional plugins that provide encrypted connections,
authentication, authorization and access control:

- `X-Pack <https://www.elastic.co/products/x-pack>`_, an Elastic
  commercial plugin with free trial period. Supports encryption,
  authentication, access control, integrates with Kibana and Logstash. Since
  the plugin is developed by the same team, its releases are in parallel with
  Elasticsearch.

- `Search Guard <https://search-guard.com/>`_, an open source third
  party plugin with commercial support. Has features comparable with X-Pack,
  with more basic features like HTTP and transport encryption, basic
  authentication and access control available free of charge.

- `ReadonlyREST <https://readonlyrest.com/>`_, an open source security plugin
  focused on the Elasticsearch HTTP REST interface security.


Standalone deployment or cluster
--------------------------------

With the default configuration, the ``debops.elasticsearch`` role will deploy
the Elasticsearch service in a "standalone" mode without exposing the service
to the outside world. This allows easy deployments for development or testing
purposes.

In production environment, you are strongly advised to deploy Elasticsearch on
at least three (3) nodes to ensure consistency in the cluster. To enable
cluster mode, you will need to configure the firewall for Elasticsearch and use
one or multiple Ansible inventory groups to design your cluster architecture.

The role currently does not support deployment of multiple Elasticsearch
instances on one host. As an alternative, consider setting up an internal
container environment with each Elasticsearch instance in a separate container
with its own IP address or use `Elastic Cloud Elasticsearch Service
<https://www.elastic.co/cloud/elasticsearch-service>`_ which does this for you and more.

See the :ref:`elasticsearch__ref_clustering` for more details.


Use as a role dependency
------------------------

The Elasticsearch main configuration file
`does not support an include statement or conf.d directory <https://github.com/elastic/elasticsearch/issues/11362>`_.
To mitigate that and allow multiple Elasticsearch configuration sources from
other Ansible roles, the ``debops.elasticsearch`` role supports operation as
a dependent role. This functionality can be used by other Ansible roles to
better manage Elasticsearch plugins or extend the cluster configuration without
the need to implement the entire role again and with preserved idempotency.

See the :ref:`elasticsearch__ref_dependency` for more details.


Example inventory
-----------------

To deploy Elasticsearch in a standalone mode, you can add the host to the
``[debops_service_elasticsearch]`` Ansible inventory group:

.. code-block:: none

   [debops_service_elasticsearch]
   hostname

The default playbook supports use of different Ansible inventory groups for
different types of Elasticsearch nodes.
See :ref:`elasticsearch__ref_clustering` for more details.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.elasticsearch`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/elasticsearch.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::elasticsearch``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::elasticsearch:config``
  Generate the Elasticsearch configuration taking into account different
  configuration sources.
