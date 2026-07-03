.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _elasticsearch__ref_upgrades:

Elasticsearch Upgrade Notes
===========================

Here you can find tips and notes related to upgrading Elasticsearch over
different releases using DebOps. The roles currently should be able to manage
Elasticsearch v6.8.x release and newer.

.. only:: html

   .. contents::
      :local:


Elasticsearch v6.8.x and older
------------------------------

The Elasticsearch v6.8.x release is the first release with support for X-Pack
Security features for free, namely TLS encryption and user authentication.
However in 2026, it's a bit difficult to install due to the Elastic APT
repositories for this release using an unsupported GPG keys.

Basic install without TLS or user authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's use a simple environment with 3 Elasticsearch hosts and 1 Kibana host,
all included in the ``[elastic]`` Ansible inventory group. An example
inventory:

.. code-block:: none

   [debops_all_hosts]
   es1       ansible_host=es1.example.org
   es2       ansible_host=es2.example.org
   es3       ansible_host=es3.example.org
   kibana    ansible_host=kibana.example.org

   [elastic]
   es1
   es2
   es3
   kibana

   [debops_service_elastic_co:children]
   elastic

   [debops_service_elasticsearch]
   es1
   es2
   es3

   [debops_service_kibana]
   kibana

To allow use of old GPG in APT repositories on newer Debian releases, we can
configure the APT crypto policies using the :ref:`debops.resources` role,
included by default in the DebOps :file:`common.yml` playbook (the file below
is included in DebOps documentation of the :ref:`debops.elasticsearch` role,
for convenience).

.. literalinclude:: examples/resources-apt-policy.yml
   :language: yaml
   :lines: 1,6-

The :ref:`debops.elastic_co` DebOps role can configure Elastic APT repositories
not included in the :command:`extrepo` database. For this to work, we need to
specify the desired APT repository version in the inventory and disable the
:ref:`debops.extrepo` configuration included in the :ref:`debops.elasticsearch`
and the :ref:`debops.kibana` roles.

.. code-block:: yaml

   ---
   # inventory/group_vars/elastic/elastic_co.yml

   # Disable Elastic repository managed by extrepo
   elasticsearch__extrepo__dependent_sources: []
   kibana__extrepo__dependent_sources: []

   # Select Elasticsearch v6.8.x release
   elastic_co__version: '6.x'

The Elasticsearch v6.8.x version requires Java 8 to work correctly. This
version of OpenJDK is not available in Debian repositories, but an external
`Eclipse Temurin`__ OpenJDK 8 can be used instead. This can be configured in
the :ref:`debops.java` role, used in the Elasticsearch playbook.

.. __: https://adoptium.net/temurin

.. code-block:: yaml

   ---
   # inventory/group_vars/elastic/java.yml

   java__flavor: 'temurin'
   java__temurin_version: '8'

You have to explicitly configure the :ref:`debops.elasticsearch` role to
disable X-Pack support and user authentication. At the same time, we set up an
Elasticsearch cluster and allow connections on the local network through the
firewall.

.. code-block:: yaml

   ---
   # inventory/group_vars/elasticsearch.yml

   # Disable TLS encryption and user account support in Elasticsearch
   elasticsearch__xpack_enabled: False

   # Disable user account creation in the role itself
   elasticsearch__authentication_enabled: False

   # Enable anonymous access to be able to use Kibana UI
   elasticsearch__authentication_anonymous_access: True

   # Allow connections to the ES cluster through the firewall
   elasticsearch__allow_tcp:  [ '192.0.2.0/24' ]
   elasticsearch__allow_http: [ '192.0.2.0/24' ]

   # Make sure that Elasticsearch listens on local network
   elasticsearch__network_host: [ '_local_', '_site_' ]

   # Specify the initial master nodes to expect by Elasticsearch
   elasticsearch__initial_master_nodes: [ 'es1', 'es2', 'es3' ]

   # Set the first node as the API endpoint to use (no encryption!)
   elasticsearch__api_base_url: 'http://es1.example.org:9200'

And to finish off, configure Kibana to expect no encryption.

.. code-block:: yaml

   ---
   # inventory/group_vars/elastic/kibana.yml

   # Disable X-Pack Security support (only relevant on Kibana <8.0.0)
   kibana__security_enabled: False

   # Enable anonymous access to Elasticsearch cluster to turn off the login
   # form in Kibana
   kibana__elasticsearch_anonymous_access: True

   # Point Kibana to unencrypted Elasticsearch cluster
   kibana__elasticsearch_url: 'http://es1.example.org:9200'
   kibana__elasticsearch_hosts: [ 'http://es1.example.org:9200' ]

This configuration should create an Elasticsearch v6.8.x installation with
unencrypted connections and without user authentication. After initial
deployment of hosts using your preferred method (by hand, Terraform,
cloud-init, etc.), run the DebOps commands to setup the hosts:

.. code-block:: console

   user@controller:~$ debops run bootstrap -l elastic -u root ; \
                      debops run common -l elastic ; \
                      debops run service/elastic_co -l elastic ; \
                      debops run service/elasticsearch -l elastic ; \
                      debops run service/kibana -l elastic

Afterwards, you should be able to reach Kibana at https://kibana.example.org/
URL, or similar depending on your additional configuration. Note that the
access to the Kibana website is encrypted with HTTPS, while the inter-cluster
communication is done over HTTP (no encryption).

Enabling TLS encryption and user authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You should be able to enable both TLS encryption and user authentication at
once, however to ensure a controlled state of the cluster, it can be done as
separate steps outlined below.

First, enable inter-cluster TLS communication by changing in the configuration
files:

.. code-block:: yaml

   ---
   # inventory/group_vars/elasticsearch.yml

   # Set the value to True (default) or remove
   elasticsearch__xpack_enabled: True

   # Set the first node as the API endpoint to use
   elasticsearch__api_base_url: 'https://es1.example.org:9200'

.. code-block:: yaml

   ---
   # inventory/group_vars/elastic/kibana.yml

   # Set the value to True (default) or remove
   kibana__security_enabled: True

   # Point Kibana to encrypted Elasticsearch cluster
   kibana__elasticsearch_url: 'https://es1.example.org:9200'
   kibana__elasticsearch_hosts: [ 'https://es1.example.org:9200' ]

After making changes, apply them to the cluster:

.. code-block:: console

   user@controller:~$ debops run service/elasticsearch \
                                 service/kibana -l elastic --diff

When the changes are applied, you should be able to connect to the ES cluster
via the Kibana UI as before. You can verify the state of the cluster by logging
in to one of the hosts and running a command:

.. code-block:: none

   user@es1:~$ curl -k https://localhost:9200/_cluster/health

WHen everything works as expected, you can enable user authentication:

.. code-block:: yaml

   ---
   # inventory/group_vars/elasticsearch.yml

   # Set to True (default) or remove
   elasticsearch__authentication_enabled: True

   # Set to False (default) or remove
   elasticsearch__authentication_anonymous_access: False

.. code-block:: yaml

   ---
   # inventory/group_vars/elastic/kibana.yml

   Set to False (default) or remove
   kibana__elasticsearch_anonymous_access: False

After making changes, apply them to the cluster:

.. code-block:: console

   user@controller:~$ debops run service/elasticsearch \
                                 service/kibana -l elastic --diff

When the Ansible finishes execution, after reloading the Kibana web page you
should see the login form. You can try accessing the Elasticsearch cluster with
the user 'elastic' and password automatically gneerated and stored in the
:file:`secret/elasticsearch/credentials/` subdirectory, located in the DebOps
project directory.
