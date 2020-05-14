.. Copyright (C) 2020 Pedro Luis Lopez <pedroluis.lopezsanchez@gmail.com>
.. Copyright (C) 2020 Innobyte Bechea Leonardo <https://www.innobyte.com/>
.. Copyright (C) 2020 Innobyte Alin Alexandru <https://www.innobyte.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Default variable details
========================

Some of ``debops.influxdb_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _influxdb_server__ref_options:

influxdb_server__default_configuration
--------------------------------------

Controls how the HTTP endpoints are configured. These are the primary
mechanism for getting data into and out of InfluxDB.

.. code-block:: yaml

   influxdb_server__default_configuration:

     - name: 'http'
       options:
         - bind-address: '"{{ influxdb_server__bind }}:{{ influxdb_server__port }}"'
         - https-enabled: '{{ "true" if influxdb_server__pki else "false" }}'
         - auth-enabled: 'true'

Syntax
~~~~~~

The variables are YAML lists, each list entry is a YAML dictionary that uses
specific parameters:

``name``
    Required. This parameter defines the option name, and it needs to be unique in a given configuration file

  ``options``
      Optional. A YAML list of :command:`influxdb` configuration options defined in the configuration file.

      Each element of the options list is a YAML dictionary with specific parameters.

      For more information, refer to the InfluxDB documentation at
      https://docs.influxdata.com/influxdb/latest/administration/config/

Examples
~~~~~~~~

.. code-block:: yaml

    influxdb_server__default_configuration:

      - name: 'global'
        options:
          - reporting-disabled: 'true'
          - bind-address: '"{{ influxdb_server__rpc_bind }}:{{ influxdb_server__rpc_port }}"'

      - name: 'meta'
        options:
          - dir: '"{{ influxdb_server__directory }}/meta"'

      - name: 'data'
        options:
          - dir: '"{{ influxdb_server__directory }}/data"'
          - wal-dir: '"{{ influxdb_server__directory }}/wal"'

      - name: 'coordinator'
        options: []

      - name: 'retention'
        options: []

      - name: 'shard-precreation'
        options: []

      - name: 'monitor'
        options: []

      - name: 'http'
        options:
          - bind-address: '"{{ influxdb_server__bind }}:{{ influxdb_server__port }}"'
          - https-enabled: '{{ "true" if influxdb_server__pki else "false" }}'
          - auth-enabled: 'true'

      - name: 'logging'
        options: []

      - name: 'subscriber'
        options: []

      - name: 'graphite'
        options: []

      - name: 'collectd'
        options: []

      - name: 'opentsdb'
        options: []

      - name: 'udp'
        options: []

      - name: 'continuous_queries'
        options: []

      - name: 'tls'
        options:
          - min-version: '"tls1.2"'
