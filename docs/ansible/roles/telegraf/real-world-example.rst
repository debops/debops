.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Real world use
==============

Telegraf requires at least one input and output defined. 
Default ``debops.telegraf`` role variables create two plugins with nearly zero
practical use, these are dummy input and output plugins only to fullfill minimal
Telegraf configuration requirements. 

These dummy examples are inactivated automatically if you declare any content
to variable ``telegraf__configuration``.

In next few paragraphs it will be shown real world use example.

.. _telegraf__ref_options:

Configuration
-------------

Telegraf instance consists of four types of plugins: ``input``, ``output``,
``aggregator`` and ``processor`` ones. Only one input and one output is mandatory,
but you are able to define unlimited amount of plugins in one instance. 

Syntax
~~~~~~

The variables are YAML lists, each list entry is a YAML dictionary that uses
specific parameters:

``name``
    Required. This parameter defines the option name, and it needs to be unique
    in a given configuration file. This name will represent filename in telegraf
    configuration directory.

    It is recommended to avoid using whitespaces and other special characters, 
    use just plain alphabet and numbers and ``_``.

``config``
    Required. It's a TOML syntax which defines a plugin according to Telegraf
    documentation. It's just being copied without modifification into
    configuration directory as a separate file. 

    For more information, refer to the Telegraf documentation at
    https://docs.influxdata.com/telegraf/

``state``
    Optional. By default ``present``. If you declare it as ``absent``, this
    plugin will be removed from your Telegraf instance configuration and
    disactivated.

If you configure your instance and later remove one or more of plugins from your
ansible configuration, it will be automatically disactivated in the host
and backuped to a filename ending ``.inactive``, for your future reference.  

Examples
~~~~~~~~

This example shows real world case of defining an input plugin which receives
stream of UDP data from Collectd and forwards it into InfluxDB 2.0 instance.

.. code-block:: yaml

 telegraf__configuration:
   - name: 'telegraf2influxdb'
     config: |
       [[outputs.influxdb_v2]]
         urls = ["http://127.0.0.1:8086"]
         token = "4bwv8cXllnYz7KXakKMz173YPSaSOH5_E70FE01PkXf3a7IC-IrzP-zCqjOtU1NGJiZycLguRhuDl8cUpz9QFw=="
         organization = "DebOps"
         bucket_tag = "bucket4debops"
         exclude_bucket_tag = true
     state: 'present'

   - name: 'udp4collectd'
     config: |
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
to a particular host only.

.. code-block:: yaml

  telegraf__configuration: []

  telegraf__host_configuration:
    - name: 'input_system'
      config: |
        [[inputs.system]]
      state: 'present'

    - name: 'input_diskio'
      config: |
        [[inputs.diskio]]
          devices = ["nvme0n1", "nvme1n1", "md10"]
      state: 'present'

    - name: 'input_net'
      config: |
        [[inputs.net]]
          interfaces = ["eth0", "bridge0"]
      state: 'present'

    - name: 'input_zfs'
      config: |
        [[inputs.zfs]]
          poolMetrics = true
          datasetMetrics = true
      state: 'present'

