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
  :file:`<name>.yml` scrape configuration file of the instance. Without it,
  the instance does not scrape anything, but it can still receive data through
  the push protocols enabled with ``flags``.

``global``
  Optional. Dictionary written to the ``global`` section of the scrape
  configuration file, for example with the ``external_labels`` added to all
  samples scraped by the instance.

``flags``
  Optional. Dictionary with :command:`vmagent` command line flags of the
  instance, without the leading ``-``. It's combined with
  :envvar:`vmagent__default_flags` and :envvar:`vmagent__flags`, and takes
  precedence over them. The flags are rendered as follows:

  - ``True`` is rendered as ``-<key>``;
  - ``False`` is rendered as ``-<key>=false``;
  - a list is rendered as a repeated ``-<key>=<value>`` flag;
  - ``null`` removes a flag defined in the default flags;
  - other values are rendered as ``-<key>=<value>``.

  The flags are passed to the daemon through the ``ARGS`` variable in the
  :file:`<name>.env` file, therefore the values cannot contain whitespace or
  the ``"`` character. Use the configuration files referenced by the flags for
  more complex settings.

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
           static_configs:
             - targets:
                 - 'switch01.example.org:9116'
                 - 'switch02.example.org:9116'
       flags:
         httpListenAddr: '127.0.0.1:8430'
         remoteWrite.maxDiskUsagePerURL: '8GB'
         promscrape.suppressScrapeErrors: True


.. _vmagent__ref_scrape_configs:

vmagent__scrape_configs
-----------------------

The scrape jobs of the ``default`` instance are defined in the following lists,
concatenated in this order into :envvar:`vmagent__combined_scrape_configs`:

- :envvar:`vmagent__default_scrape_configs`, defined by the role (empty by
  default);
- :envvar:`vmagent__scrape_configs`, for all hosts in the inventory;
- :envvar:`vmagent__group_scrape_configs`, for hosts in an inventory group;
- :envvar:`vmagent__host_scrape_configs`, for specific hosts;
- :envvar:`vmagent__dependent_scrape_configs`, defined by other Ansible roles
  in the playbook.

Each element is a Prometheus scrape job, written to the scrape configuration
file without changes; see the `vmagent documentation
<https://docs.victoriametrics.com/victoriametrics/sd_configs/>`_ for the
supported parameters. Since the lists are concatenated, two jobs with the same
``job_name`` on different levels are both written to the file, and
:command:`vmagent` rejects such configuration. The file is checked with
:command:`vmagent -dryRun` before it's installed.

Example: scrape ``node_exporter`` on all hosts and an additional exporter on
the database servers:

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

Instances defined in :envvar:`vmagent__instances` and the related lists use
their own ``scrape_configs`` parameter instead.


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
