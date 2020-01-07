Default variable details
========================

Some of ``debops.elasticsearch`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _elasticsearch__ref_configuration:

elasticsearch__configuration
----------------------------

The ``elasticsearch__*_configuration`` variables define the Elasticsearch
configuration options that are set in the
:file:`/etc/elasticsearch/elasticsearch.yml` configuration file.

The main Elasticsearch configuration file format is YAML.
The `reference documentation <https://www.elastic.co/guide/en/elasticsearch/reference/current/settings.html>`_
defines two YAML formats recognized by Elasticsearch, hierarchical (YAML
dictionary keys are indented), or flat (YAML dictionary keys are separated by
dots). This role focuses only on the latter, flat format since it's used
everywhere in the Elasticsearch documentation and seems to be the preferred
method for the majority of the configuration options.

For quick reference, the Elasticsearch configuration file contains options in the
following format:

.. code-block:: yaml

   cluster.name: example-cluster
   node.name: node-1
   network.host: [ _local_, _site_ ]
   bootstrap.memory_lock: true
   discovery.zen.minimum_master_nodes: 3

The ``elasticsearch__*_configuration`` variables are YAML lists of
dictionaries. Each YAML dictionary defines an option, or redefines a previously
defined option (the variables are flattened and then processed in order).

The first YAML dictionary key of each option (in above case, ``cluster``,
``node``, ``network``, ``bootstrap``, ``discovery`` is significant, and is used
to separate configuration options into sections defined by the
:envvar:`elasticsearch__configuration_sections` variable.

Configuration options can be defined as YAML dictionaries directly, with the
key being the name of the option, and value being its value:

.. code-block:: yaml

   elasticsearch__configuration:
     - 'cluster.name': 'example-cluster'
     - 'node.name': 'node-1'
     - 'network.host': [ '_local_', '_site_' ]
     - 'bootstrap.memory_lock': True
     - 'discovery.zen.minimum_master_nodes': 3

The extended YAML dictionary format is detected if a YAML dictionary contains
a ``name`` key. The dictionaries support specific parameters:

``name``
  String. The name of the Elasticsearch option.

``value``
  The value of the Elasticsearch option. Can be a string, a number, a boolean
  or a YAML list.

``comment``
  An optional comment added to the option, either as a string or a YAML text
  block.

``state``
  If not specified or ``present``, the option will be included in the
  configuration. If ``absent``, the option will not be included. If
  ``comment``, the option will be present but commented out (it's an internal
  feature and may not work reliably for all cases).

``options``
  Optional, a YAML dictionary with keys being the "leaf" configuration names of
  the primary key, and value being their values. This parameter can be used to
  group several similar configuration options together in the generated
  configuration file, for readability. When this parameter is used, the "leaf"
  part of the main configuration name is discarded, and only used as a marker
  for these parameters. An example configuration:

  .. code-block:: yaml

     elasticsearch__configuration:
       - name: 'node.meta.host_type'
         comment: 'Node type'
         options:
           'master': True
           'data':   True
           'ingest': True

  The above configuration should result in:

  .. code-block:: yaml

     # Node type
     node.master: true
     node.data: true
     node.ingest: true

``raw``
  Optional, a YAML text block. The name of the configuration option will be
  discarded and used only as a marker for these parameters. The contents of the
  ``raw`` key will be added as-is to the configuration file. You can use this
  to include more extensive configuration defined as a hierarchical YAML
  structure. An example configuration which should be equivalent to the
  previous example:

  .. code-block:: yaml

     elasticsearch__configuration:
       - name: 'node.meta.host_type'
         raw: |
           # Node type
           node.master: true
           node.data: true
           node.ingest: true

You should make sure that the indentation of the YAML parameters is consistent
through the configuration file.


.. _elasticsearch__ref_configuration_sections:

elasticsearch__configuration_sections
-------------------------------------

The :file:`/etc/elasticsearch/elasticsearch.yml` configuration file is
structured in informal 'sections", each section contains configuration options
from a specific group (``node``, ``cluster``, etc.). The
:envvar:`elasticsearch__configuration_sections` contains a YAML list of
sections and option types to associate with them. The order of the entries on
the list determines the order of the sections in the finished configuration
file.

Each section definition is a YAML dictionary with specific parameters:

``name``
  Name of the section, stored as a comment.

``part`` or ``parts``
  A string or a YAML list of configuration option prefixes (first YAML
  dictionary key of a given configuration option). Only the parts defined for
  a given section will be included in that section.

After all of the sections are processed, any left over configuration options
not matched with a particular section will be added at the end of the
configuration file.


.. _elasticsearch__ref_plugins:

elasticsearch__plugins
----------------------

The ``elasticsearch__*_plugins`` variables are YAML lists that can be used to
install or remove Elasticsearch plugins. Support for plugin management using
these variables is minimalistic; you can install plugins known by the Elastic
`plugin repository <https://www.elastic.co/guide/en/elasticsearch/plugins/current/index.html>`_,
or from an URL. More involved management can be done by creating a separate
role and using ``debops.elasticsearch`` as a role dependency to manage
configuration if necessary. See :ref:`elasticsearch__ref_dependency` for more
details.

Each element of the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the plugin that shows up in the output of the

  .. code-block:: console

     bin/elasticsearch-plugin list

  command. This parameter will be used to check the state of the plugin.

``url``
  Optional. If the plugin is distributed via an URL, you can provide it here
  for the plugin management script to use instead of the plugin name.

``state``
  Optional. If not specified or ``present``, the plugin and its configuration
  will be installed. If ``absent`` the plugin and its configuration will be
  removed.

``configuration`` or ``config``
  Optional. Custom configuration for a given plugin, in the format recognized
  by the main configuration template.

  See :ref:`elasticsearch__ref_configuration` for more details.

Examples
~~~~~~~~

Install Java Script language support:

.. code-block:: yaml

   elasticsearch__plugins:
     - name: 'lang-javascript'
