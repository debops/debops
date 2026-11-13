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

`vmagent <https://docs.victoriametrics.com/victoriametrics/vmagent/>`_ is
a small metrics agent from the VictoriaMetrics project. It scrapes
Prometheus-compatible exporters (and accepts metrics over several push
protocols), applies optional relabeling, and forwards the samples to one or
more ``-remoteWrite.url`` endpoints. The samples are kept in an on-disk
persistent queue while the remote storage is unavailable.

The ``debops.vmagent`` role installs :command:`vmagent` and manages one or more
named instances through the ``vmagent@.service`` systemd template unit
(``vmagent@<name>.service``).


Installation
------------

The VictoriaMetrics project does not provide an APT repository; the
:command:`vmagent` binary is published in the ``vmutils`` release archives on
the `GitHub Releases page
<https://github.com/VictoriaMetrics/VictoriaMetrics/releases>`_. Debian also
ships :command:`vmagent` in the ``victoria-metrics`` package, but in an older
version and together with the VictoriaMetrics database server and its service.

The role downloads the release archive for :envvar:`vmagent__version`, checks
it against the SHA256 checksum in :envvar:`vmagent__archive_sha256_map`, and
installs the ``vmagent-prod`` binary as :envvar:`vmagent__bin_path`, in the
directory for local binaries defined by the :ref:`debops.fhs` role
(:file:`/usr/local/bin/` by default). The archive is staged in the cache
directory defined by the same role and removed after the installation. The
persistent queues stay in :file:`/var/lib/vmagent/`, the home directory of the
``_vmagent`` system account, because they are state of the daemon and not user
data. On hosts without Internet access the
archive can be copied from the Ansible Controller or downloaded from an internal
mirror, and the installation can be skipped when the binary is a part of the
host image. See :ref:`vmagent__ref_guide_airgapped` for details.


Minimal inventory
-----------------

To manage :command:`vmagent` on a host, add it to the
``[debops_service_vmagent]`` Ansible inventory group:

.. code-block:: yaml

   debops_service_vmagent:
     children:
       debops_all_hosts:

The ``default`` instance is created when the remote write endpoint is set, for
example in the :file:`group_vars/all/vmagent.yml` file:

.. code-block:: yaml

   vmagent__remote_write_urls:
     - 'https://vmetrics.example.org/api/v1/write'

   vmagent__scrape_configs:
     - job_name: 'node'
       static_configs:
         - targets: [ '127.0.0.1:9100' ]

This creates the ``vmagent@default.service`` instance on each host, which
scrapes the local ``node_exporter`` and sends the samples to
``vmetrics.example.org``. The ``default`` instance adds the ``host`` label with
the inventory name of the host to all scraped samples, see
:envvar:`vmagent__external_labels`, so the samples of the ``node`` job from
different hosts stay separate although each host scrapes the same
``127.0.0.1:9100`` target.


Scrape configuration
--------------------

The scrape jobs of the ``default`` instance are collected from the
:envvar:`vmagent__default_scrape_configs`, :envvar:`vmagent__scrape_configs`,
:envvar:`vmagent__group_scrape_configs`, :envvar:`vmagent__host_scrape_configs`
and :envvar:`vmagent__dependent_scrape_configs` lists, in that order. A job
with a new ``job_name`` is added to the jobs defined earlier, and a job with
the same ``job_name`` is merged with the earlier one, so the host variables can
change a job defined for all hosts or remove it with ``state: 'absent'``.
Other Ansible roles can add their jobs through
:envvar:`vmagent__dependent_scrape_configs` in the playbook. See
:ref:`vmagent__ref_scrape_configs` for details.

Before a new scrape configuration file replaces the current one, it is checked
with :command:`vmagent -dryRun`, so a job with an unknown parameter stops the
play instead of the instance.


Multiple instances
------------------

Each instance is a separate :command:`vmagent` process with its own scrape
configuration, remote write endpoints and persistent queue directory. Use
:envvar:`vmagent__instances` (or the group and host variants) to define
additional instances:

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
         - name: 'httpListenAddr'
           value: '127.0.0.1:8430'
         - name: 'remoteWrite.maxDiskUsagePerURL'
           value: '8GB'

All instances listen on ``127.0.0.1:8429`` by default, therefore each
additional instance needs its own ``httpListenAddr`` flag with a separate port.
The role stops with an error when two instances on a host use the same port.
The flags of an
instance are added to the flags defined for all instances in
:envvar:`vmagent__flags` and the related lists, see :ref:`vmagent__ref_flags`.

Instance entries with the same ``name`` are merged together, so the host
variables can change an instance defined for all hosts, including the
``default`` instance. See :ref:`vmagent__ref_instances` for the supported
parameters.


Secret management
-----------------

When an instance sets ``bearer_token: True``, the role copies the
:file:`secret/vmagent/instances/<name>/bearer_token` file from the
:ref:`debops.secret` directory on the Ansible Controller to
:file:`/etc/vmagent/<name>.token` on the host, readable by the ``_vmagent``
group, and adds the ``-remoteWrite.bearerTokenFile`` flag to the command
line. The token is used for all remote write URLs of the instance. The role
stops with an error that shows the expected path when the file does not
exist; create it before running the playbook, for example:

.. code-block:: console

   $ mkdir -p -m 0700 ansible/secret/vmagent/instances/longterm
   $ (umask 077; editor ansible/secret/vmagent/instances/longterm/bearer_token)

The exact path of the :file:`secret/` directory depends on the project layout.


Configuration changes
---------------------

When only the scrape configuration of an instance changes, the role reloads
the instance (:command:`vmagent` re-reads the file after the ``SIGHUP``
signal). Changes of the command line flags or the bearer token restart only
the affected instance, other instances on the host are not touched. An upgrade
of the binary or a change of the template unit restarts all instances on the
host. An instance which still runs a replaced binary, for example because an
earlier run failed before the restart, is found through the local facts and
restarted on the next run.


The systemd unit
----------------

The ``vmagent@.service`` template unit runs the instances as the ``_vmagent``
UNIX account, restarts them on failure, gives them 30 seconds to flush the
queues on shutdown and allows 65536 open files. The access of the daemon to the
system is restricted; only the queue directory of the instance is writable.

To change these settings, create a drop-in file with the :ref:`debops.systemd`
role. A drop-in for ``vmagent@.service`` applies to all instances, a drop-in for
``vmagent@<name>.service`` only to the given instance:

.. code-block:: yaml

   systemd__units:

     - name: 'vmagent@.service.d/limits.conf'
       raw: |
         [Service]
         LimitNOFILE=262144
       state: 'present'

     - name: 'vmagent@longterm.service.d/network.conf'
       raw: |
         [Service]
         IPAddressDeny=any
         IPAddressAllow=localhost 192.0.2.0/24
       state: 'present'
       restart: 'vmagent@longterm.service'

The ``restart`` parameter of the :ref:`debops.systemd` role takes a single unit
name. After a change of a drop-in for ``vmagent@.service``, restart all
instances to apply it, for example with
:command:`systemctl restart 'vmagent@*.service'`.

The HTTP endpoint of :command:`vmagent` (metrics, ``/-/reload``,
``/api/v1/import``) listens on the loopback address. The default port 8429 is
registered in :file:`/etc/services` by the :ref:`debops.etc_services` role.


Example playbook
----------------

If you are using this role without DebOps, here is an example Ansible
playbook that uses the ``debops.vmagent`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/vmagent.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution.

Available role tags:

``role::vmagent``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::vmagent``
  Skip the main role tasks, but run the role dependencies, for example the
  :ref:`debops.etc_services` role.

``meta::facts``
  Update the Ansible local facts of the role.
