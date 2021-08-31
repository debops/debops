.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Real world use
==============

Telegraf requires at least one input and output defined. 
Default ``debops.telegraf`` role variables create two plugins with nearly zero
practical use, these are dummy input and output plugins only to fullfill minimal
Telegraf configuration requirements. 

In next few paragraphs it will be shown real world use example.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _telegraf__ref_options:

Plugins
-------

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

``content``
    Required. It's a TOML syntax which defines a plugin according to Telegraf
    documentation. It's just being copied without modifification into
    configuration directory as a separate file. 

    For more information, refer to the Telegraf documentation at
    https://docs.influxdata.com/telegraf/

``state``
    Optional. By default ``present``. If you declare it as ``absent``, this
    plugin will be removed from your Telegraf instance configuration and
    disactivated.

Examples
~~~~~~~~

This example shows real world case of defining an input plugin which receives
stream of UDP data from Traefik web proxy and forwards it into InfluxDB 2.0 instance.

.. code-block:: yaml

  telegraf__plugins_input:
    - '{{ telegraf__input_traefik }}'

  telegraf__plugins_output:
    - '{{ telegraf__output_influxdb2 }}'

  telegraf__input_traefik:
    name: 'input_udp_traefik'
    content: |
      [[inputs.socket_listener]]
        service_address = "udp4://:12105"
        data_format = "influx"
        content_encoding = "identity"
        [inputs.socket_listener.tags]
          bucket4itz = "traefik"
    state: 'present'

  telegraf__output_influxdb2:
    name: 'output_influx2'
    content: |
      [[outputs.influxdb_v2]]
        urls = ["http://127.0.0.1:8086"]
        token = "4bwv88XllnYz7KXakKMz173YPsfSOH5_E70FE01PkXf3a7IC-IrzD-zCqjOtU1NGJtZycLguFhuDl8cUpz9QFw=="
        organization = "DebOps"
        bucket_tag = "bucket4itz"
        exclude_bucket_tag = true
    state: 'present'
