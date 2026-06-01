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

The :envvar:`vmagent__default_instances`,
:envvar:`vmagent__instances`,
:envvar:`vmagent__group_instances`, and
:envvar:`vmagent__host_instances` lists define vmagent instances managed
by the role. They are combined into
:envvar:`vmagent__combined_instances` and processed in order.

Each list entry is a dictionary with the following supported keys:

``name``
  Required. The name of the instance. Used as the systemd instance
  identifier (``vmagent@<name>.service``) and as the base name for
  configuration files (``<name>.yml``, ``<name>.env``) and the
  persistent queue directory (:file:`{vmagent__home}/{name}/`).

``state``
  Optional, default: ``present``. If ``absent``, the instance is
  stopped, disabled and its configuration / queue files are removed.

``remote_write_urls``
  Required for ``state: present``. List of URLs passed to vmagent as
  repeating ``-remoteWrite.url`` flags. At least one entry is required;
  vmagent will fan-out the same samples to every URL in parallel.

``scrape_configs``
  Optional, default: ``[]``. Prometheus-format ``scrape_configs`` list
  rendered into :file:`{vmagent__config_dir}/{name}.yml`. When empty,
  vmagent starts with no scrape targets; it can still serve any of the
  push protocols enabled via ``flags``.

``global``
  Optional. Mapping rendered into the ``global:`` section of the
  scrape config file. Use for ``external_labels`` shared by all jobs in
  this instance.

``flags``
  Optional. Mapping of additional vmagent command-line flags merged
  on top of :envvar:`vmagent__instance_default_flags`. Per-instance
  ``flags`` take precedence. Rendering rules:

  * ``True`` -> ``-<key>``
  * ``False`` -> flag omitted
  * scalar value -> ``-<key>=<value>``
  * list value -> repeated ``-<key>=<v1> -<key>=<v2> ...``

``bearer_token``
  Optional, default: ``False``. When set to ``True``, the role copies
  the file at
  :file:`secret/{vmagent__secret_base_path}/{name}/bearer_token` on the
  Ansible Controller to
  :file:`{vmagent__home}/{name}/bearer_token` on the host and adds
  ``-remoteWrite.bearerTokenFile=...`` to the command line.

Example - one local-scrape instance and one cluster-aggregator instance
on the same host:

.. code-block:: yaml

   vmagent__host_instances:

     - name: 'default'
       remote_write_urls:
         - 'https://vmetrics.example.org/api/v1/write'
       scrape_configs:
         - job_name: 'node'
           static_configs:
             - targets: [ '127.0.0.1:9100' ]
       global:
         external_labels:
           dc: 'fra1'
           role: 'app'

     - name: 'aggregator'
       remote_write_urls:
         - 'https://vmetrics.example.org/api/v1/write'
       bearer_token: True
       scrape_configs:
         - job_name: 'switches'
           static_configs:
             - targets:
                 - 'switch01.example.org:9116'
                 - 'switch02.example.org:9116'
       flags:
         remoteWrite.maxDiskUsagePerURL: '8GB'
         promscrape.suppressScrapeErrors: True


.. _vmagent__ref_binary_source:

Binary source selection (waterfall)
-----------------------------------

The role evaluates the following sources, in order, and uses the first
one that resolves successfully. The detailed mechanics live in
:file:`tasks/install_binary.yml`; the rules below summarize the user
contract.

#. ``vmagent__skip_install: True`` - the role does not touch
   :envvar:`vmagent__bin_path`. Useful when the binary is provided by
   a Packer-built image or an external package.

#. The binary at :envvar:`vmagent__bin_path` already reports the
   matching :envvar:`vmagent__version` (parsed from
   ``vmagent -version``). The install stage short-circuits with no
   downloads.

#. :envvar:`vmagent__local_archive_path` (non-empty) points at a
   release archive already on the remote host. The role does not copy
   the archive but still verifies its SHA256 before extracting.

#. :envvar:`vmagent__controller_archive_path` (non-empty) points at a
   release archive on the Ansible Controller. The role copies it into
   :envvar:`vmagent__cache_dir` with :command:`ansible.builtin.copy`,
   then verifies and extracts.

#. None of the above: the role downloads
   :envvar:`vmagent__release_url`
   (= ``{{ vmagent__release_base_url }}/v{{ vmagent__version }}/{{ vmagent__release_archive_name }}``)
   with :command:`ansible.builtin.get_url`. Inline checksum verification
   uses :envvar:`vmagent__archive_sha256`.

See the :ref:`vmagent__ref_guide_airgapped` guide for end-to-end
examples of each pattern.


.. _vmagent__ref_systemd_hardening_extra:

vmagent__systemd_hardening_extra
--------------------------------

The role ships a hardened ``vmagent@.service`` template unit:
``ProtectSystem=strict``, ``PrivateTmp``, ``ProtectKernelTunables``,
empty ``CapabilityBoundingSet``, ``MemoryDenyWriteExecute``, and
several others (see
:file:`templates/etc/systemd/system/vmagent@.service.j2`). The unit's
state directory is constrained to :file:`{vmagent__home}/%i`, which is
the only path the daemon needs to write to.

To add further restrictions without forking the template, append
``[Service]`` directives via
:envvar:`vmagent__systemd_hardening_extra`:

.. code-block:: yaml

   vmagent__systemd_hardening_extra:
     - 'IPAddressAllow=10.0.0.0/8 127.0.0.0/8'
     - 'IPAddressDeny=any'
     - 'SystemCallFilter=@system-service'
     - 'SystemCallFilter=~@privileged @resources'

The directives are emitted verbatim at the end of the ``[Service]``
block, so any ``systemd`` directive is supported.
