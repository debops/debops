.. Copyright (C) 2026 Patryk Sciborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _prometheus_exporter__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _prometheus_exporter__ref_exporters:

prometheus_exporter__exporters
------------------------------

The :envvar:`prometheus_exporter__exporters`,
:envvar:`prometheus_exporter__group_exporters` and
:envvar:`prometheus_exporter__host_exporters` lists define the managed
exporters. They are combined into
:envvar:`prometheus_exporter__combined_exporters`.

Each entry is a dict with the following keys:

``name``
  Required. Short exporter name, e.g. ``node``, ``postgres``, ``sql``. Used
  to derive defaults for ``package``, ``service``, ``bin_path`` and the
  listen port.

``state``
  Optional, default ``present``. ``absent`` stops/disables the service and
  removes the drop-in (and purges the package when
  :envvar:`prometheus_exporter__purge_on_absent` is True).

``package`` / ``packages``
  Optional. APT package (default ``prometheus-<name>-exporter``) and a list
  of extra packages.

``service`` / ``bin_path``
  Optional. systemd unit (default ``prometheus-<name>-exporter``) and binary
  path (default ``/usr/bin/<service>``).

``listen_address``
  Optional. ``host:port`` for ``--web.listen-address``. Defaults to
  ``prometheus_exporter__default_listen_host`` plus the port from
  :envvar:`prometheus_exporter__known_ports` for this ``name``.

``web_listen_flag``
  Optional, default ``--web.listen-address``. Override for exporters that use
  a different flag name.

``args``
  Optional list of extra command-line flags appended verbatim.

``environment``
  Optional dict of environment variables placed in the drop-in (e.g.
  ``DATA_SOURCE_NAME``). When non-empty, the drop-in is written with mode
  ``0600`` and ``no_log``.

``config`` / ``config_path`` / ``config_flag`` / ``config_mode`` / ``config_no_log``
  Optional. When ``config`` (a dict) is set, it is rendered as YAML to
  ``config_path`` (default ``/etc/prometheus/<name>.yml``) and
  ``<config_flag>=<config_path>`` (default ``--config.file``) is added to
  the command line. Use ``config_mode: '0600'`` and ``config_no_log: true``
  when the file contains secrets (e.g. ``prometheus-sql-exporter`` DSN).

``config_files``
  Optional list of extra files (``{ path, content|src, mode }``) for
  exporters split across multiple files.

``systemd_overrides``
  Optional list of extra ``[Service]`` lines, e.g.
  ``AmbientCapabilities=CAP_NET_RAW`` (blackbox ICMP) or ``User=root``
  (local IPMI).

Example:

.. code-block:: yaml

   prometheus_exporter__group_exporters:

     - name: 'node'

     - name: 'postgres'
       environment:
         DATA_SOURCE_NAME: 'host=127.0.0.1 port=5432 user=prometheus_exporter password=SECRET dbname=postgres sslmode=disable'
