.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.kibana`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _kibana__ref_configuration:

kibana__configuration
---------------------

The ``kibana__*_configuration`` variables define the Kibana configuration
options that are set in the :file:`/etc/kibana/kibana.yml` configuration file.

The main Kibana configuration file format is YAML.
The `reference documentation <https://www.elastic.co/guide/en/kibana/current/settings.html>`_
defines two YAML formats recognized by Kibana, hierarchical (YAML dictionary
keys are indented), or flat (YAML dictionary keys are separated by dots). This
role focuses only on the latter, flat format since it's used everywhere in the
Kibana documentation and seems to be the preferred method for majority of the
configuration options.

For quick reference, Kibana configuration file contains options in the
following format (similar to Elasticsearch):

.. code-block:: yaml

   cluster.name: example-cluster
   node.name: node-1
   network.host: [ _local_, _site_ ]
   bootstrap.memory_lock: true
   discovery.zen.minimum_master_nodes: 3

The ``kibana__*_configuration`` variables are a YAML lists of dictionaries.
Each YAML dictionary defines an option, or redefines a previously defined
option (the variables are flattened and then processed in order).

The first YAML dictionary key of each option (in above case, ``cluster``,
``node``, ``network``, ``bootstrap``, ``discovery`` is significant, and is used
to separate configuration options into sections defined by the
:envvar:`kibana__configuration_sections` variable.

Configuration options can be defined as YAML dictionaries directly, with the
key being the name of the option, and value being its value:

.. code-block:: yaml

   kibana__configuration:
     - 'cluster.name': 'example-cluster'
     - 'node.name': 'node-1'
     - 'network.host': [ '_local_', '_site_' ]
     - 'bootstrap.memory_lock': True
     - 'discovery.zen.minimum_master_nodes': 3

The extended YAML dictionary format is detected if a YAML dictionary contains
a ``name`` key. The dictionaries support specific parameters:

``name``
  String. The name of the Kibana option.

``value``
  The value of the Kibana option. Can be a string, a number, a boolean or
  a YAML list.

``comment``
  An optional comment added to the option, either as a string or a YAML text
  block.

``state``
  If not specified or ``present``, the option will be included in the
  configuration. If ``absent``, the option will not be included. If
  ``comment``, the option will be present but commented out (it's an internal
  feature and may not work reliably for all cases).

``raw``
  Optional, a YAML text block. The name of the configuration option will be
  discarded and used only as a marker for these parameters. The contents of the
  ``raw`` key will be added as-is to the configuration file. You can use this
  to include more extensive configuration defined as a hierarchical YAML
  structure. An example configuration which should be equivalent to the
  previous example:

  .. code-block:: yaml

     kibana__configuration:
       - name: 'node.meta.host_type'
         raw: |
           # Node type
           node.master: true
           node.data: true
           node.ingest: true

You should make sure that the indentation of the YAML parameters is consistent
through the configuration file.


.. _kibana__ref_configuration_sections:

kibana__configuration_sections
------------------------------

The :file:`/etc/kibana/kibana.yml` configuration file is structured in informal
'sections", each section contains configuration options from a specific group
(``node``, ``cluster``, etc.). The :envvar:`kibana__configuration_sections`
contains a YAML list of sections and option types to associate with them. The
order of the entries on the list determines the order of the sections in the
finished configuration file.

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


.. _kibana__ref_plugins:

kibana__plugins
---------------

The ``kibana__*_plugins`` variables are YAML lists that can be used to
install or remove Kibana plugins. Support for plugin management using
these variables is minimalistic; you can install plugins known by the Elastic
`plugin repository <https://www.elastic.co/guide/en/kibana/current/kibana-plugins.html>`_,
or from an URL. More involved management can be done by creating a separate
role and using ``debops.kibana`` as a role dependency to manage
configuration if necessary. See :ref:`kibana__ref_dependency` for more
details.

Each element of the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the plugin that shows up in the output of the

  .. code-block:: console

     bin/kibana-plugin list

  command, without the version information included. This parameter will be
  used to check the state of the plugin.

``url``
  Optional. If the plugin is distributed via an URL, you can provide it here
  for the plugin management script to use instead of the plugin name.

``state``
  Optional. If not specified or ``present``, the plugin and its configuration
  will be installed. If ``absent`` the plugin and its configuration will be
  removed.

``state``
  Optional. The system user used for plugin management. Defaults to :envvar:`kibana__user`.
  Certain plugins like X-Pack generate files on installation which Kibana needs
  to have write permissions to.


``configuration`` or ``config``
  Optional. Custom configuration for a given plugin, in the format recognized
  by the main configuration template.

  See :ref:`kibana__ref_configuration` for more details.

Examples
~~~~~~~~

Install a LogTrail plugin:

.. code-block:: yaml

   kibana__plugins:
     - name: 'logtrail'
       url: 'https://github.com/sivasamyk/logtrail/releases/download/0.1.13/logtrail-5.4.0-0.1.13.zip'


.. _kibana__ref_keys:

kibana__keys
------------

The ``kibana__*_keys`` variables define the contents of the `Kibana keystore`__
used to keep confidential data like passwords or access tokens. The keys can be
referenced in the Kibana configuration files using the ``${secret_key}``
syntax.

.. __: https://www.elastic.co/guide/en/kibana/current/secure-settings.html

Examples
~~~~~~~~

Add an Elasticsearch password used for access over a secure connection. The
password is retrieved from the :file:`secret/` directory on the Ansible
Controller, managed by the :ref:`debops.secret` Ansible role:

.. code-block:: yaml

   kibana__keys:

     - ELASTIC_PASSWORD: '{{ lookup("file", secret + "/elastic-stack/elastic/password") }}'

Update an existing key with new content (presence of the ``force`` parameter
will update the key on each Ansible run):

.. code-block:: yaml

   kibana__keys:

     - name: 'ELASTIC_PASSWORD'
       value: 'new-elasticsearch-password'
       force: True

Remove a key from the Kibana keystore:

.. code-block:: yaml

   kibana__keys:

     - name: 'ELASTIC_PASSWORD'
       state: 'absent'

Syntax
~~~~~~

Each key entry is defined by a YAML dictionary. The keys can be defined using
a simple format, with dictionary key being the secret key name, and its value
being the secret value. In this case you should avoid the ``name`` or ``value``
as the secret keys.

Alternatively, secret keys can be defined using YAML dictionaries with specific
parameters:

``name``
  Required. Name of the secret key to store in the Kibana keystore.

``value``
  Optional. A string with the value which should be stored under a given key.

``state``
  Optional. If not specified or ``present``, the key will be inserted into the
  keystore. If ``absent``, the key will be removed from the keystore.

``force``
  Optional, boolean. If present and ``True``, the specified key will be updated
  in the keystore.
