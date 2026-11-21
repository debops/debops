.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _vmagent__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.vmagent`` default variables have more extensive
configuration than simple strings or lists, here you can find
documentation and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _vmagent__ref_instances:

vmagent__instances
------------------

The :envvar:`vmagent__default_instances`, :envvar:`vmagent__instances`,
:envvar:`vmagent__group_instances` and :envvar:`vmagent__host_instances` lists
define the :command:`vmagent` instances managed by the role. They are combined
into :envvar:`vmagent__combined_instances` and parsed by the
``debops.debops.parse_kv_items`` filter: entries with the same ``name`` are
merged together, and parameters of a later entry replace the parameters of an
earlier one. A parameter with a nested value, for example ``flags`` or
``scrape_configs``, is replaced as a whole.

The :envvar:`vmagent__default_instances` list defines the ``default`` instance,
built from :envvar:`vmagent__remote_write_urls` and the scrape configuration
lists described in :ref:`vmagent__ref_scrape_configs`. It's created only when
:envvar:`vmagent__remote_write_urls` is not empty.

Each list entry is a dictionary with the following parameters:

``name``
  Required. Name of the instance, used as the systemd instance name
  (``vmagent@<name>.service``), as the base name of the configuration files
  (:file:`<name>.yml`, :file:`<name>.env` and :file:`<name>.token` in
  :envvar:`vmagent__config_dir`) and as the name of the persistent queue
  directory in :envvar:`vmagent__home`. The name can contain letters, digits,
  and the ``.``, ``_`` and ``-`` characters, and has to start with a letter or
  a digit.

``state``
  Optional. If not specified or ``present``, the instance is configured and
  started. If ``absent``, the instance is stopped and disabled, and its
  configuration files and persistent queue are removed. If ``init``, the
  instance is defined but not managed until a later entry with the same
  ``name`` changes its state. If ``ignore``, the entry is not evaluated.

``remote_write_urls``
  Required for instances in the ``present`` state. List of URLs passed to
  :command:`vmagent` as the ``-remoteWrite.url`` flags. :command:`vmagent`
  sends all samples to each URL, with a separate persistent queue for each one.

``scrape_configs``
  Optional. List of Prometheus scrape jobs written to the
  :file:`<name>.yml` scrape configuration file of the instance. Jobs with the
  same ``job_name`` are merged together, see :ref:`vmagent__ref_scrape_configs`
  for details. Without it, the instance does not scrape anything, but it can
  still receive data through the push protocols enabled with ``flags``.

``global``
  Optional. Dictionary written to the ``global`` section of the scrape
  configuration file, for example with the ``external_labels`` added to all
  samples scraped by the instance. The ``default`` instance sets it from
  :envvar:`vmagent__external_labels`. A ``global`` parameter in a later entry
  of the ``default`` instance replaces it as a whole, therefore it needs to
  repeat the ``host`` label when the label should be kept.

``flags``
  Optional. List of :command:`vmagent` command line flags of the instance, in
  the format described in :ref:`vmagent__ref_flags`. It's added after
  :envvar:`vmagent__combined_flags`, therefore its entries take precedence over
  the flags defined for all instances.

``bearer_token``
  Optional, boolean. If ``True``, the role copies the
  :file:`secret/{vmagent__secret_base_path}/{name}/bearer_token` file from the
  Ansible Controller to :file:`{vmagent__config_dir}/{name}.token` on the host,
  and uses it with the ``-remoteWrite.bearerTokenFile`` flag. The file needs to
  exist before the role is applied. If the parameter is changed to ``False``,
  the token is removed from the host.

Examples
~~~~~~~~

Enable authentication of the ``default`` instance on a specific host; the entry
is merged with the ``default`` instance defined by the role:

.. code-block:: yaml

   vmagent__host_instances:

     - name: 'default'
       bearer_token: True

Add an instance which scrapes network switches and sends the samples with
a larger persistent queue, next to the ``default`` instance:

.. code-block:: yaml

   vmagent__host_instances:

     - name: 'switches'
       remote_write_urls:
         - 'https://vmetrics.example.org/api/v1/write'
       bearer_token: True
       global:
         external_labels:
           site: 'fra1'
       scrape_configs:
         - job_name: 'snmp'
           metrics_path: '/snmp'
           params:
             module: [ 'if_mib' ]
           static_configs:
             - targets:
                 - 'switch01.example.org'
                 - 'switch02.example.org'
           relabel_configs:
             - source_labels: [ '__address__' ]
               target_label: '__param_target'
             - source_labels: [ '__param_target' ]
               target_label: 'instance'
             - target_label: '__address__'
               replacement: '127.0.0.1:9116'
       flags:
         - name: 'httpListenAddr'
           value: '127.0.0.1:8430'
         - name: 'remoteWrite.maxDiskUsagePerURL'
           value: '8GB'
         - name: 'promscrape.suppressScrapeErrors'
           value: True


.. _vmagent__ref_flags:

vmagent__flags
--------------

The :command:`vmagent` command line flags of each instance are defined in the
following lists, combined in this order:

- :envvar:`vmagent__default_flags`, defined by the role;
- :envvar:`vmagent__flags`, for all hosts in the inventory;
- :envvar:`vmagent__group_flags`, for hosts in an inventory group;
- :envvar:`vmagent__host_flags`, for specific hosts;
- the ``flags`` parameter of the instance, see :ref:`vmagent__ref_instances`.

The first four lists apply to all instances on a host. The combined list is
parsed by the ``debops.debops.parse_kv_config`` filter: entries with the same
``name`` are merged together, so a later entry changes the value of a flag
defined earlier or removes it. Each entry is a dictionary with the following
parameters:

``name``
  Required. Name of the flag, without the leading ``-``, for example
  ``httpListenAddr``.

``value``
  Required for the flag to be included, in this entry or in an earlier entry
  with the same ``name``; an entry in the ``present`` state without ``value``
  brings back the value of an earlier entry. The value of an entry in the
  ``absent`` state is not used. The value is rendered as follows:

  - ``True`` is rendered as ``-<name>``;
  - ``False`` is rendered as ``-<name>=false``;
  - a list is rendered as a repeated ``-<name>=<value>`` flag;
  - other values are rendered as ``-<name>=<value>``.

  The value of a later entry replaces the value of an earlier entry as
  a whole, also when one of them is a list. The elements of a list are
  rendered in the given order, including repeated elements, because
  :command:`vmagent` pairs the flags which apply to each remote write URL,
  for example ``remoteWrite.basicAuth.username``, with the
  ``-remoteWrite.url`` flags by position. An empty list replaces an earlier
  value and the flag is not rendered; for ``httpListenAddr`` this means the
  default ``:8429`` address of :command:`vmagent`.

``state``
  Optional. If not specified or ``present``, the flag is included. If
  ``absent``, the flag is not included, which removes a flag with the same name
  defined earlier, for example one of the flags defined by the role. If
  ``init``, the flag is defined but not included until a later entry changes
  its state. If ``ignore``, the entry is not evaluated by the role. An entry
  without ``state`` keeps the state of an earlier entry with the same name, or
  ``present`` if there is none; an entry which should bring back a flag
  removed earlier, for example in the group inventory, needs
  ``state: 'present'``.

The flags are passed to the daemon through the ``ARGS`` variable in the
:file:`<name>.env` file and split on whitespace by systemd, which also removes
quotes, therefore the values cannot contain whitespace, the ``"`` and ``'``
characters or the ``\`` character; the role stops with an error when they do.
Use the configuration files referenced by the flags for more complex settings.

Examples
~~~~~~~~

Suppress the scrape error messages on all hosts, use a larger persistent queue
on the hosts in the ``collectors`` group, and turn the error messages back on
for one of these hosts:

.. code-block:: yaml

   # group_vars/all/vmagent.yml
   vmagent__flags:
     - name: 'promscrape.suppressScrapeErrors'
       value: True

   # group_vars/collectors/vmagent.yml
   vmagent__group_flags:
     - name: 'remoteWrite.maxDiskUsagePerURL'
       value: '8GB'

   # host_vars/collector01.example.org/vmagent.yml
   vmagent__host_flags:
     - name: 'promscrape.suppressScrapeErrors'
       state: 'absent'

Listen on the IPv4 and IPv6 loopback addresses; ``httpListenAddr`` accepts
more than one value:

.. code-block:: yaml

   vmagent__host_flags:
     - name: 'httpListenAddr'
       value: [ '127.0.0.1:8429', '[::1]:8429' ]


.. _vmagent__ref_scrape_configs:

vmagent__scrape_configs
-----------------------

The scrape jobs of the ``default`` instance are defined in the following lists,
combined in this order into :envvar:`vmagent__combined_scrape_configs`:

- :envvar:`vmagent__default_scrape_configs`, defined by the role (empty by
  default);
- :envvar:`vmagent__scrape_configs`, for all hosts in the inventory;
- :envvar:`vmagent__group_scrape_configs`, for hosts in an inventory group;
- :envvar:`vmagent__host_scrape_configs`, for specific hosts;
- :envvar:`vmagent__dependent_scrape_configs`, defined by other Ansible roles
  in the playbook.

Each element is a Prometheus scrape job; see the `vmagent documentation
<https://docs.victoriametrics.com/victoriametrics/sd_configs/>`_ for the
supported parameters. Each job needs the ``job_name`` parameter, the role
stops with an error when it's missing. The combined list is parsed by the
``debops.debops.parse_kv_items`` filter, with ``job_name`` as the key: jobs
with the same ``job_name`` are merged together, and the parameters of a later
job replace the parameters of an earlier one. A parameter is replaced as
a whole, for example a new ``static_configs`` list replaces the list defined
earlier. The jobs are written to the scrape configuration file in the order
in which they first appear in the lists.

The role uses the ``state`` parameter of a job and removes it before the job
is written to the file, together with the ``comment``, ``weight`` and
``anchor_to`` parameters of the filter:

``state``
  Optional. If not specified or ``present``, the job is written to the file.
  If ``absent``, the job is not written to the file, which removes a job with
  the same ``job_name`` defined earlier. If ``init``, the job is defined but
  not written to the file until a later entry changes its state. If
  ``ignore``, the entry is not evaluated by the role. An entry without
  ``state`` keeps the state of an earlier entry with the same ``job_name``;
  an entry which should bring back a job removed earlier needs
  ``state: 'present'``.

The file is checked with :command:`vmagent -dryRun` before it's installed.

Example: scrape ``node_exporter`` on all hosts and an additional exporter on
the database servers, use a different exporter port on one of them, and skip
the exporter on another one:

.. code-block:: yaml

   # group_vars/all/vmagent.yml
   vmagent__scrape_configs:
     - job_name: 'node'
       static_configs:
         - targets: [ '127.0.0.1:9100' ]

   # group_vars/databases/vmagent.yml
   vmagent__group_scrape_configs:
     - job_name: 'postgres'
       static_configs:
         - targets: [ '127.0.0.1:9187' ]

   # host_vars/db01.example.org/vmagent.yml
   vmagent__host_scrape_configs:
     - job_name: 'postgres'
       static_configs:
         - targets: [ '127.0.0.1:9188' ]

   # host_vars/db02.example.org/vmagent.yml
   vmagent__host_scrape_configs:
     - job_name: 'postgres'
       state: 'absent'

Instances defined in :envvar:`vmagent__instances` and the related lists use
their own ``scrape_configs`` parameter instead, where jobs with the same
``job_name`` are merged in the same way.


.. _vmagent__ref_binary_source:

Binary source
-------------

The role checks the following cases in order and stops at the first one
that applies:

#. ``vmagent__skip_install: True`` - the role does not touch
   :envvar:`vmagent__bin_path`. Useful when the binary is provided by the host
   image or a different package.

#. The binary at :envvar:`vmagent__bin_path` already reports the matching
   :envvar:`vmagent__version` (parsed from ``vmagent -version``). Nothing is
   copied or downloaded. A binary which does not report any version is not
   replaced; the role stops with an error instead.

#. :envvar:`vmagent__controller_archive_path` is not empty. The role verifies
   the SHA256 checksum of that file on the Ansible Controller and copies it to
   :envvar:`vmagent__cache_dir` on the host.

#. Otherwise the role downloads :envvar:`vmagent__release_url`, by default
   from the GitHub Releases page, with :command:`ansible.builtin.get_url`,
   which verifies the download against :envvar:`vmagent__archive_sha256`. The
   URL can point at an internal mirror, or use the ``file://`` scheme for an
   archive which is already present on the host.

In both cases the ``vmagent-prod`` binary is extracted from the archive and
installed as :envvar:`vmagent__bin_path`, and the archive is removed
afterwards, also when the installation fails. The instances are restarted
after the binary is installed or upgraded.

See the :ref:`vmagent__ref_guide_airgapped` guide for examples.
