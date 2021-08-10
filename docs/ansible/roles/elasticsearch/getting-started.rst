.. Copyright (C) 2014-2016 Nick Janetakis <nick.janetakis@gmail.com>
.. Copyright (C) 2014-2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2014-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Upstream package is used by default
-----------------------------------

The :ref:`debops.elasticsearch` role depends on the :ref:`debops.extrepo`
Ansible role to configure access to the Elastic.co APT repository. This means
that usually the latest available Elasticsearch release will be installed by
default. If you require older releases, you can use the
:ref:`debops.apt_preferences` role to select the desired package version.

Alternatively, you can "mask" the
:envvar:`elasticsearch__extrepo__dependent_sources` variable in the Ansible
inventory and configure the APT repositories yourself via the :ref:`debops.apt`
role.


Elasticsearch is insecure in standalone mode
--------------------------------------------

The Elasticsearch service in the default configuration supports only plaintext
connections between the standalone host and clients. There's no client
authentication or authorization policies as well. Due to that you should take
care to not expose your standalone Elasticsearch service to the outside world
without proper encryption and authentication.

In cluster mode, and with :ref:`debops.pki` role configured on the host, the
:ref:`debops.elasticsearch` role will automatically enable the `X-Pack`__
plugin and configure TLS encryption for HTTP clients and Transport
communication between cluster nodes. This is possible due to changes in the
Elastic licensing (the default installation comes with the Basic subscription
which provides support for TLS and user/group management via the X-Pack
plugin).

.. note:: User and role management is not implement yet. Refer to the
   Elasticsearch documentation for details about enabling this manually.

.. __: https://www.elastic.co/products/x-pack/

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
   :lines: 1,7-


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
