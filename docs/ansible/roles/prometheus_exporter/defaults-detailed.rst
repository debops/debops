.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
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

The exporters are defined in the following lists, combined in this order into
:envvar:`prometheus_exporter__combined_exporters`:

- :envvar:`prometheus_exporter__default_exporters`, defined by the role (empty
  by default);
- :envvar:`prometheus_exporter__exporters`, for all hosts in the inventory;
- :envvar:`prometheus_exporter__group_exporters`, for hosts in an inventory
  group;
- :envvar:`prometheus_exporter__host_exporters`, for specific hosts.

The combined list is parsed by the ``debops.debops.parse_kv_items`` filter
(see :ref:`universal_configuration`). Entries with the same ``name`` are
merged together: a parameter of a later entry replaces the same parameter of
an earlier one, except ``environment`` and ``configuration``, whose entries
are merged by their own ``name`` (see below). A host can therefore change one
environment variable or one configuration section of an exporter defined for
a group, or disable that exporter with ``state: absent``, without repeating
the rest of its definition.

Each entry is a dictionary with the following parameters:

``name``
  Required. Short exporter name, for example ``node``, ``postgres`` or
  ``sql``. It's used to derive the defaults of the ``package``, ``service``
  and ``bin_path`` parameters and the listen port. An entry can also be just
  the name as a string.

``state``
  Optional. If not specified or ``present``, the exporter is installed and
  started. If ``absent``, the service is stopped and disabled, the drop-in,
  the environment file and the configuration files managed by the role are
  removed and the package is purged when
  :envvar:`prometheus_exporter__purge_on_absent` is ``True``. If ``init``, the
  exporter is defined, but not managed, until a later entry sets
  ``state: present``. If ``ignore``, the entry is skipped.

  An entry without ``state`` keeps the state of the earlier entry with the
  same name. An exporter set to ``absent`` in one list stays ``absent`` when
  a later list adds parameters to it, unless that list sets
  ``state: present``. The same applies to an ``init`` exporter and to the
  entries of the ``environment`` and ``configuration`` lists.

``package`` / ``packages``
  Optional. The APT package of the exporter (default
  ``prometheus-<name>-exporter``) and a list of additional packages.

``service`` / ``bin_path``
  Optional. The systemd unit of the exporter (default
  ``prometheus-<name>-exporter``) and its binary (default
  ``/usr/bin/<service>``).

``listen_address``
  Optional when ``name`` is in :envvar:`prometheus_exporter__known_ports`.
  The ``host:port`` address passed to ``--web.listen-address``. By default
  it's :envvar:`prometheus_exporter__default_listen_host` and the known port.
  The role stops with an error when an exporter which is not in
  :envvar:`prometheus_exporter__known_ports` does not set it.

``web_listen_flag``
  Optional, default ``--web.listen-address``. The command line flag which sets
  the listen address, for exporters which use a different name.

``args``
  Optional. List of additional command line flags, passed in the given
  order.

``allow``
  Optional. List of IP addresses or CIDR subnets allowed to connect to the
  exporter, added to :envvar:`prometheus_exporter__allow`,
  :envvar:`prometheus_exporter__group_allow` and
  :envvar:`prometheus_exporter__host_allow`. It matters only when the
  ``listen_address`` is not a loopback address, see
  :ref:`prometheus_exporter__ref_firewall`.

``environment``
  Optional. List of environment variables of the exporter, for example
  ``DATA_SOURCE_NAME``. Each entry is a dictionary with the following
  parameters:

  ``name``
    Required. The name of the variable: letters, digits and ``_``, not
    starting with a digit.

  ``value``
    Required. The value of the variable, a string or a number.

  ``state``
    Optional. If not specified or ``present``, the variable is set. If
    ``absent``, a variable defined in an earlier entry is removed. ``init``
    and ``ignore`` work as described in :ref:`universal_configuration`.

  The variables are written to the :file:`<config_dir>/<name>.env` file
  (mode ``0600``, owned by ``root``), which is loaded by the drop-in with
  ``EnvironmentFile=``. Unlike ``Environment=``, the values are not visible
  to other local users through the systemd D-Bus interface. The task which
  writes the file hides its output, unless ``debops__no_log`` is ``False``.
  The file is removed when the list has no variables.

``configuration``
  Optional. List of sections of the configuration file of the exporter. Each
  entry is a dictionary with the following parameters:

  ``name``
    Required. The name of the section, used only to merge the entries; it's
    not written to the file.

  ``config``
    Required. A dictionary merged with the dictionaries of the other entries
    by the ``combine(recursive=True)`` filter. A key in a later entry replaces
    the same key in an earlier one, nested dictionaries are merged and lists
    are replaced as a whole. For example, a later entry with a list of
    ``blackbox`` modules replaces the whole list. Entries with the same
    ``name`` are not merged key by key; the ``config`` dictionary of the
    later entry replaces the earlier one.

  ``state``
    Optional. If not specified or ``present``, the section is included. If
    ``absent``, a section defined in an earlier entry is removed. ``init``
    and ``ignore`` work as described in :ref:`universal_configuration`.

  If the merged dictionary is not empty, it's written as YAML to
  ``config_path`` and ``<config_flag>=<config_path>`` is added to the command
  line.

``config_path`` / ``config_flag``
  Optional. The path of the configuration file (default
  :file:`/etc/prometheus/<name>.yml`) and the command line flag which points
  the exporter to it (default ``--config.file``). The drop-in replaces the
  command line of the package, including the configuration file set in its
  :file:`/etc/default/` file. An exporter which needs a configuration file,
  like ``blackbox``, needs either the ``configuration`` list or
  ``config_path`` set explicitly; without ``configuration`` the role passes
  that path to the exporter but does not manage the file, so it can point to
  the file shipped by the package, for example
  :file:`/etc/prometheus/blackbox.yml`.

``config_mode`` / ``config_group``
  Optional. The mode (default ``0644``) and the group (default ``root``) of
  the configuration file and of the ``config_files``. The files are owned by
  ``root``. The Debian packages usually run the exporters as an unprivileged
  user, therefore the default mode allows everyone to read the files. Keep
  the passwords in ``environment``. When a password has to be in the
  configuration file, set ``config_mode: '0640'`` and ``config_group`` to the
  group of the service (usually ``prometheus``). The ``0600`` mode works only
  when the exporter can read a file owned by ``root``.

``config_no_log``
  Optional, default ``False``. If ``True``, the tasks which write and remove
  the configuration file and the ``config_files`` hide their output, for
  example when the configuration contains a database password. The
  ``debops__no_log`` variable set to ``False`` shows the output again, for
  debugging.

``config_files``
  Optional. List of additional files, for exporters with a configuration
  split into more than one file. Each entry is a dictionary with the
  ``path``, ``content`` or ``src``, ``mode`` and ``group`` parameters;
  ``group`` defaults to ``config_group``. The list is replaced as a whole by
  a later entry of the exporter.

Changing the systemd unit
~~~~~~~~~~~~~~~~~~~~~~~~~

The role writes the :file:`override.conf` drop-in of each exporter and replaces
its ``ExecStart=`` and ``EnvironmentFile=`` options. Other changes of the
service, for example additional capabilities of the ``blackbox`` exporter for
ICMP probes, are made with separate drop-in files managed by the
:ref:`debops.systemd` role:

.. code-block:: yaml

   systemd__units:

     - name: 'prometheus-blackbox-exporter.service.d/capabilities.conf'
       raw: |
         [Service]
         AmbientCapabilities=CAP_NET_RAW
       state: 'present'
       restart: 'prometheus-blackbox-exporter.service'

Examples
~~~~~~~~

Install the ``node`` and ``postgres`` exporters on a group of hosts:

.. code-block:: yaml

   prometheus_exporter__group_exporters:

     - name: 'node'

     - name: 'postgres'
       environment:

         - name: 'DATA_SOURCE_NAME'
           value: 'host=127.0.0.1 port=5432 user=prometheus_exporter password=SECRET dbname=postgres sslmode=disable'

Configure the ``blackbox`` exporter on a group of hosts, then change the
timeout of one module and remove the ICMP module on one host:

.. code-block:: yaml

   prometheus_exporter__group_exporters:

     - name: 'blackbox'
       configuration:

         - name: 'http'
           config:
             modules:
               http_2xx:
                 prober: 'http'
                 timeout: '5s'

         - name: 'icmp'
           config:
             modules:
               icmp:
                 prober: 'icmp'

   prometheus_exporter__host_exporters:

     - name: 'blackbox'
       configuration:

         - name: 'http-timeout'
           config:
             modules:
               http_2xx:
                 timeout: '10s'

         - name: 'icmp'
           state: 'absent'

Disable the ``node`` exporter on one host:

.. code-block:: yaml

   prometheus_exporter__host_exporters:

     - name: 'node'
       state: 'absent'


.. _prometheus_exporter__ref_firewall:

prometheus_exporter__allow
--------------------------

By default the exporters listen on loopback and the firewall is not changed.
An exporter which listens on another address, for example
``listen_address: '0.0.0.0:9100'`` or ``'[::]:9100'``, gets a rule in
:ref:`debops.ferm` (see :envvar:`prometheus_exporter__ferm__dependent_rules`)
which accepts connections to its port only from the addresses in
:envvar:`prometheus_exporter__allow`,
:envvar:`prometheus_exporter__group_allow`,
:envvar:`prometheus_exporter__host_allow` and the ``allow`` parameter of the
exporter. If the combined list is empty, the rule is not created and the port
stays closed. The rule is removed when the list becomes empty, when the
exporter moves back to loopback and when it's set to ``absent``.

Allow a central Prometheus server to scrape the ``node`` exporter directly:

.. code-block:: yaml

   prometheus_exporter__group_exporters:

     - name: 'node'
       listen_address: '0.0.0.0:9100'
       allow: [ '192.0.2.10' ]
