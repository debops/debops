Guides and examples
===================

.. include:: includes/all.rst

.. contents::
   :local:
   :depth: 2

.. _elasticsearch__ref_node_types:

Elasticsearch Node Types
------------------------

Below is a breakdown of how you can use groups to allocate different node
types to a number of servers. If all you want to do is use ES as a single
server dependency in another role then include the role in your role's
meta main file. You don't have to add the groups in your inventory in that
case.

The Elasticsearch upstream configuration has two settings, ``node.master`` and
``node.data``. A combination of those settings being ``True`` or ``False``
determines what type of node your server will be.

Master servers (``node.master: True`` and ``node.data: True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the default setting for all nodes in Elasticsearch.

.. code-block:: none

    [debops_service_elasticsearch_master]
    apple
    orange
    banana

Workhorse servers (``node.master: False`` and ``node.data: True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The server will never become a master but it will hold data.

.. code-block:: none

    [debops_service_elasticsearch_workhorse]
    red
    blue

Coordinator servers (``node.master: True`` and ``node.data: False``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A coordinator can become master but it doesn't store data. Its goal is to
always have a lot of free resources.

.. code-block:: none

    [debops_service_elasticsearch_coordinator]
    nyancat

Search load balancer servers (``node.master: False`` and ``node.data: False``)

.. _elasticsearch__ref_host_groups:

Inventory host groups
---------------------

It's always useful to have a common group that composes everything.
Elasticsearch will be installed on any server that belongs to any of the above
groups.

This group would mainly be used for firewall settings which would apply to
all of your ES nodes. It does not control whether or not ES gets installed.

.. code-block:: none

    [debops_elasticsearch:children]
    debops_elasticsearch_master
    debops_elasticsearch_workhorse
    debops_elasticsearch_coordinator
    debops_elasticsearch_loadbalancer

They are just shortcuts to setting the two node settings for you. You don't
have to use the extra groups. By all means create custom groups and set the
variables yourself if you want.

You can also edit the defaults to use your own custom group names and still
get the benefits of group based node type separation.

Example configuration
---------------------

.. code-block:: yaml

    elasticsearch_bind_host: ['0.0.0.0']
    elasticsearch_node_allow: '{{ groups["debops_elasticsearch"] }}'
    elasticsearch_http_allow: '{{ groups["your_web_apps"] }}'

The above example tells ES to accept connections from anywhere and then white
lists your ES group so they can all talk to each other

In addition to that is white lists your app servers so they can access the ES
HTTP API to actually query ES.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
