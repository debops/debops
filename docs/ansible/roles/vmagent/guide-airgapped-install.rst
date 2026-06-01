.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _vmagent__ref_guide_airgapped:

Guide: air-gapped / no-GitHub installs
======================================

.. only:: html

   .. contents::
      :local:


Overview
--------

The role downloads the ``vmagent`` binary from the upstream
VictoriaMetrics GitHub Releases by default. Many production environments
restrict outbound traffic from managed hosts and cannot reach GitHub
directly. The role supports four additional delivery channels, evaluated
in a strict waterfall (first match wins) inside
:file:`tasks/install_binary.yml`:

#. :envvar:`vmagent__skip_install` - the role manages no binary at all.
#. The :envvar:`vmagent__bin_path` already contains the matching version
   - the role short-circuits to a no-op.
#. :envvar:`vmagent__local_archive_path` - a release archive already
   present on the remote host.
#. :envvar:`vmagent__controller_archive_path` - a release archive copied
   from the Ansible Controller.
#. :envvar:`vmagent__release_url` - downloaded with
   :command:`ansible.builtin.get_url` from
   :envvar:`vmagent__release_base_url` (GitHub by default).

The expected SHA256 checksum is enforced in every code path -
:command:`get_url` enforces it inline, while local-host and
controller-side archives are checked via a separate
:command:`ansible.builtin.stat` task with
``checksum_algorithm: sha256`` followed by an :command:`assert`. A
mismatched archive aborts the play before unpacking.


Pattern 1: internal HTTP(S) mirror (Nexus / Artifactory / MinIO)
----------------------------------------------------------------

The simplest pattern: stage the upstream archive once into your internal
artifact store, then point every host at the mirror. The role builds
the download URL as
``{{ vmagent__release_base_url }}/v{{ vmagent__version }}/{{ vmagent__release_archive_name }}``
so any storage backend that preserves the
``/v<version>/<archive>`` layout works without further changes.

.. code-block:: yaml

   vmagent__release_base_url: 'https://nexus.example.lan/raw/vendor/victoriametrics/releases'

If the mirror requires authentication, pass HTTP headers via
:envvar:`vmagent__release_url_headers`:

.. code-block:: yaml

   vmagent__release_url_headers:
     Authorization: 'Bearer {{ lookup("file", secret + "/nexus/read_token") }}'

The same SHA256 verification applies as for GitHub downloads, so the
mirror cannot silently serve a tampered archive.


Pattern 2: archive copied from the Ansible Controller
-----------------------------------------------------

For a true air-gap (no internet, no internal mirror), keep the upstream
archive in the inventory tree (optionally tracked by ``git-lfs`` so the
~100 MB tarball does not bloat the repository) and point the role at
the path on the Controller:

.. code-block:: yaml

   vmagent__controller_archive_path: '/srv/ansible/files/vmagent/vmutils-linux-amd64-v1.144.0.tar.gz'

Or, when keeping the archive inside the playbook's ``files/`` tree, use
a path resolved relative to the playbook:

.. code-block:: yaml

   vmagent__controller_archive_path: 'files/vmagent/{{ vmagent__release_archive_name }}'

The role copies the archive into :envvar:`vmagent__cache_dir` and runs
the same SHA256 assertion before extracting.


Pattern 3: archive already on the remote host
---------------------------------------------

When a host has a release archive pre-staged out of band (rsync from an
internal mirror, ``cloud-init`` user-data, etc.), point the role at it:

.. code-block:: yaml

   vmagent__local_archive_path: '/srv/depot/vmutils-linux-amd64-v1.144.0.tar.gz'

The role does not copy the archive (it is already on the host) but
still verifies its checksum before extracting.


Pattern 4: binary baked into the image (Packer)
-----------------------------------------------

When the image-build pipeline already ships
:file:`/usr/local/bin/vmagent` and you want Ansible to leave the binary
alone, opt out of installation entirely:

.. code-block:: yaml

   vmagent__skip_install: True

The role still manages the configuration, the systemd template unit,
and the per-instance lifecycle - only the binary install / verify
stage is skipped.


Proxy support
-------------

The :command:`get_url` task respects standard proxy environment
variables. Set :envvar:`vmagent__http_proxy`,
:envvar:`vmagent__https_proxy`, and :envvar:`vmagent__no_proxy` to pass
them to the task without touching the host-wide environment.

Where the project already wires proxy configuration through
``inventory__environment`` and related variables (see
:ref:`debops.environment`), the playbook-level ``environment:`` block
in :file:`playbooks/service/vmagent.yml` ensures those variables apply
to all role tasks automatically.


Updating the pinned version
---------------------------

When bumping :envvar:`vmagent__version`, update the matching SHA256
entries in :envvar:`vmagent__archive_sha256_map`. The fastest way to
obtain the new checksums is to read them from the GitHub Releases API::

   curl -fsSL https://api.github.com/repos/VictoriaMetrics/VictoriaMetrics/releases/tags/v<NEW> \
       | jq -r '.assets[] | select(.name | test("vmutils-linux-(amd64|arm64)-v[0-9.]+\\.tar\\.gz$"))
                          | "\(.name) \(.digest)"'

Mirror operators should also re-fetch and re-publish the new archives
to their internal store at the same time, otherwise the mirror's URL
will 404 until the next sync run.
