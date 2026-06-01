.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


What is vmagent?
----------------

`vmagent <https://docs.victoriametrics.com/vmagent/>`_ is a small,
write-optimized agent from the VictoriaMetrics project. It scrapes
Prometheus-compatible exporters (and accepts metrics over multiple push
protocols), applies optional relabeling, and forwards the samples to one
or more ``-remoteWrite.url`` endpoints with an on-disk persistent queue
so that data is not lost when the remote storage is briefly unavailable.

The ``debops.vmagent`` role installs vmagent natively from the upstream
VictoriaMetrics ``vmutils`` archive and manages one or more named
instances via systemd template units (``vmagent@<name>.service``).


Why not just use the APT package?
---------------------------------

VictoriaMetrics does not publish an APT repository. Official binaries are
distributed exclusively as ``.tar.gz`` archives (and ``.deb`` files
attached individually) on the
`GitHub Releases page
<https://github.com/VictoriaMetrics/VictoriaMetrics/releases>`_.
The role therefore downloads the archive directly (with mandatory SHA256
verification, see :envvar:`vmagent__archive_sha256_map`) and installs the
``vmagent-prod`` binary into :file:`/usr/local/bin/vmagent`.

For environments without GitHub access, the role supports four additional
delivery channels: an internal HTTP(S) mirror, a copy from the Ansible
Controller, a path on the remote host, or a complete bypass (when the
binary is baked into the image). See :ref:`vmagent__ref_guide_airgapped`
for details.


Prerequisites
-------------

Before using this role, you need:

1. A reachable VictoriaMetrics single-node, ``vmauth``, cluster
   ``vminsert``, or any other Prometheus-remote-write-compatible endpoint
   exposed over HTTP or HTTPS.

2. Optionally, one or more Prometheus-compatible exporters on the host
   (``node_exporter``, ``cadvisor``, ``blackbox_exporter``, ...) for
   ``vmagent`` to scrape.


Minimal inventory
-----------------

To manage vmagent on a host, add it to the ``[debops_service_vmagent]``
Ansible inventory group:

.. code-block:: yaml

   debops_service_vmagent:
     children:
       debops_all_hosts:

Minimal default configuration in ``group_vars/all/vmagent.yml``:

.. code-block:: yaml

   vmagent__default_remote_write_urls:
     - 'https://vmetrics.example.org/api/v1/write'

   vmagent__default_scrape_configs:
     - job_name: 'node'
       static_configs:
         - targets: [ '127.0.0.1:9100' ]

This creates a single ``vmagent@default.service`` on every host, scraping
the local ``node_exporter`` and remote-writing the samples to
``vmetrics.example.org``.


Multiple instances
------------------

Each instance is an independent vmagent process with its own scrape
configuration, remote-write endpoints, and persistent queue directory.
Use :envvar:`vmagent__instances` (or one of the host/group variants) to
define additional instances:

.. code-block:: yaml

   vmagent__instances:

     - name: 'longterm'
       remote_write_urls:
         - 'https://vmetrics-longterm.example.org/api/v1/write'
       bearer_token: True
       scrape_configs:
         - job_name: 'app'
           static_configs:
             - targets: [ '127.0.0.1:9091' ]
       flags:
         remoteWrite.maxDiskUsagePerURL: '8GB'

This adds a second instance (``vmagent@longterm.service``) writing into a
different VictoriaMetrics cluster with a higher local-disk buffer. The
``bearer_token: True`` flag instructs the role to deploy the matching
file from
``secret/vmagent/instances/longterm/bearer_token`` and add
``-remoteWrite.bearerTokenFile=...`` to the command line.


Secret management
-----------------

When an instance sets ``bearer_token: True``, the role uses the standard
DebOps :ref:`debops.secret` mechanism to deploy the file. Secrets live on
the Ansible Controller under :file:`secret/vmagent/instances/<name>/`
relative to the inventory root, for example::

   secret/vmagent/instances/longterm/bearer_token

The playbook pre-task ``main_env`` computes the list of required secret
directories per host, and :ref:`debops.secret` creates them on the
Controller before the main role runs.


Example playbook
----------------

If you are using this role without DebOps, here is an example Ansible
playbook that uses the ``debops.vmagent`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/vmagent.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit
what tasks are performed during an Ansible run.

Available role tags:

``role::vmagent``
  Main role tag, used in the playbook to execute all of the role tasks
  as well as role dependencies (``ansible_plugins``, ``global_handlers``,
  ``secret``).

``role::secret``
  Tag for the :ref:`debops.secret` dependency, used to (re)create the
  per-instance secret directory layout on the Ansible Controller.

``skip::vmagent``
  Skip the main role's tasks.
