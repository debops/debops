.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.telegraf`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 3


.. _telegraf__ref_configuration:

telegraf__configuration
-----------------------

The ``telegraf__configuration`` variables define the contents of the
:file:`/etc/telegraf/telegraf.conf` configuration file. The entire file is
based on a YAML configuration converted to TOML using a custom Jinja filter,
therefore the contents are limited - there's no way to add comments or comment
out sections of the file. For a more advanced configuration, you should use the
:ref:`telegraf__ref_plugins` variables instead.

.. warning:: Keep in mind that the main configuration file is world-readable.
   Use plugin files for sensitive configuration like passwords for external
   services - plugin configuration is readable only by the Telegraf UNIX
   account.

Examples
~~~~~~~~

The default configuration includes settings for the agent itself. To remove
them from the file and rely only on separate plugins directory, add in the
inventory:

.. code-block:: yaml

   telegraf__configuration:

     - name: 'agent'
       state: 'absent'

Change the agent's collection interval without modifying other parameters (note
a different ``name`` parameter which permits recursive merging of the
configuration):

.. code-block:: yaml

   telegraf__configuration:

     - name: 'agent_interval'
       config:
         agent:
           interval: '30s'
           round_interval: False

Add a set of global tags to all Telegraf instances:

.. code-block:: yaml

   telegraf__configuration:

     - name: 'global_tags'
       config:
         global_tags:
           rack: '1a'
           user: '$USER'

You can see the default list of configuration options in the
:envvar:`telegraf__default_configuration` variable.

Syntax
~~~~~~

``name``
  Required. Name of a particular configuration entry, not used otherwise.
  Configuration entries with the same ``name`` parameter are merged together an
  can affect each other.

``state``
  Optional. If not specified or ``present``, a given configuration entry will
  be included in the generated config file. If ``absent``, a given
  configuration entry will not be included in the configuration file.

``config``
  YAML dictionary with Telegraf configuration options, which will be converted
  to TOML on generation. The ``config`` parameters from multiple entries with
  the same ``name`` parameter override each other in order of appearance.

  The ``config`` parameters from different entries are combined together
  recursively, this allows modification of specific parameters in a larger
  section of the configuration file.


.. _telegraf__ref_plugins:

telegraf__plugins
-----------------

The ``telegraf__plugins`` variables define the contents of the
:file:`/etc/telegraf/telegraf.d/` configuration directory. Each configuration
entry is a separate file which can be created or removed as needed.

Examples
~~~~~~~~

The default configuration includes a ``output.discard`` output sink since the
service will not start correctly without any output configured. To comment it
out on in the generated configuration file, you can add in the inventory:

.. code-block:: yaml

   telegraf__plugins:

     - name: 'output_discard'
       state: 'comment'

Add an Elasticsearch output which uses DebOps secrets for access (you might
want to use a different account than ``elastic`` though):

.. code-block:: yaml

   - name: 'output_elasticsearch'
     config:
       outputs:
         elasticsearch:
           urls: [ 'https://es1.example.org:9200' ]
           timeout: '5s'
           enable_sniffer: False
           enable_gzip: False
           health_check_interval: '10s'
           username: 'elastic'
           password: '{{ lookup("password", secret + "/elasticsearch/"
                         + "credentials/built-in/elastic/password") }}'
           index_name: 'telegraf-%Y.%m.%d'
           manage_template: True
           template_name: 'telegraf'

This example shows real world case of defining an input plugin which receives
stream of UDP data from Collectd and forwards it into InfluxDB 2.0 instance:

.. code-block:: yaml

   telegraf__plugins:

     - name: 'telegraf2influxdb'
       raw: |
         [[outputs.influxdb_v2]]
           urls = ["http://127.0.0.1:8086"]
           token = "4bwv8cXllnYz7KXakKMz173YPSaSOH5_E70FE01PkXf3a7IC-IrzP-zCqjOtU1NGJiZycLguRhuDl8cUpz9QFw=="
           organization = "DebOps"
           bucket_tag = "bucket4debops"
           exclude_bucket_tag = true
       state: 'present'

     - name: 'udp4collectd'
       raw: |
         [[inputs.socket_listener]]
           service_address = "udp4://:25826"
           data_format = "collectd"
           content_encoding = "identity"
           ## Authentication file for cryptographic security levels
           collectd_auth_file = "/etc/collectd/passwd"
           ## One of none (default), sign, or encrypt
           collectd_security_level = "encrypt"
           ## Path of to TypesDB specifications
           collectd_typesdb = ["/usr/share/collectd/types.db"]
           collectd_parse_multivalue = "join"
           [inputs.socket_listener.tags]
             bucket4debops = "collectd"
       state: 'present'

This example defines several system monitoring input plugins which are assigned
to a particular host only:

.. code-block:: yaml

   telegraf__host_plugins:

       # Override the default configuration
     - name: 'input_system'
       raw: |
         [[inputs.system]]
       state: 'present'

     - name: 'input_diskio'
       raw: |
         [[inputs.diskio]]
           devices = ["nvme0n1", "nvme1n1", "md10"]
       state: 'present'

     - name: 'input_net'
       raw: |
         [[inputs.net]]
           interfaces = ["eth0", "bridge0"]
       state: 'present'

     - name: 'input_zfs'
       raw: |
         [[inputs.zfs]]
           poolMetrics = true
           datasetMetrics = true
       state: 'present'

You can see the default list of configured plugins in the
:envvar:`telegraf__default_plugins` variable.

Syntax
~~~~~~

The role uses :ref:`universal_configuration` system to manage Telegraf plugin
configuration files. The :envvar:`telegraf__combined_plugins` variable defines
the merge order of the plugin lists. Each variable is a list of YAML
dictionaries with specific parameters:

``name``
  Required. Name of the configuration file (the ``.conf`` extension will be
  added automatically). Multiple entries with the same ``name`` parameter will
  be merged together and can affect each other.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  generated on the host. If ``absent``, the configuration file will be removed
  from the host. If ``comment``, the file will be generated but the
  configuration itself will be commented out. If ``ignore``, a given
  configuration entry will not be processed during role execution.

``comment``
  Optional. String or YAML text block with comments about a given configuration
  file.

``config``
  YAML dictionary with Telegraf configuration options, which will be converted
  to TOML on generation. The ``config`` parameters from multiple entries with
  the same ``name`` parameter override each other in order of appearance.

``raw``
  YAML text block with Telegraf configuration in the TOML format. The ``raw``
  parameters from multiple entries with the same ``name`` parameter override
  each other in order of appearance. If both ``config`` and ``raw`` parameters
  are present, the latter takes precedence.
