.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _vmagent__ref_guide_airgapped:

Guide: installation without GitHub access
=========================================

.. only:: html

   .. contents::
      :local:


Overview
--------

By default the role downloads the ``vmutils`` release archive from the GitHub
Releases page of the VictoriaMetrics project. On hosts that cannot reach
GitHub, the archive can be downloaded from an internal mirror or copied from
the Ansible Controller, and the installation can be skipped entirely when the
binary is a part of the host image. The SHA256 checksum from
:envvar:`vmagent__archive_sha256_map` is verified for every archive, see
:ref:`vmagent__ref_binary_source` for the order in which the sources are used.


Internal HTTP(S) mirror
-----------------------

Upload the release archives to an internal artifact store and point the role
to it. The download URL is built as
``<vmagent__release_base_url>/v<vmagent__version>/<vmagent__release_archive_name>``,
so the mirror needs to keep the ``/v<version>/<archive>`` layout:

.. code-block:: yaml

   vmagent__release_base_url: 'https://mirror.example.org/victoriametrics/releases'

A mirror with a different layout can be used by setting the whole
:envvar:`vmagent__release_url` variable. The same variable accepts a
``file://`` URL of an archive already present on the host, for example
distributed by :command:`rsync` or ``cloud-init``:

.. code-block:: yaml

   vmagent__release_url: 'file:///srv/depot/{{ vmagent__release_archive_name }}'

The download respects the proxy configuration set in the
``inventory__environment`` variables, which the playbook applies to all role
tasks (see :ref:`debops.environment`).


Archive on the Ansible Controller
---------------------------------

On hosts without any access to external or internal HTTP servers, keep the
release archive on the Ansible Controller and point the role to it with an
absolute path:

.. code-block:: yaml

   vmagent__controller_archive_path: '/srv/archives/vmutils-linux-amd64-v1.156.0.tar.gz'

The checksum of the archive is verified on the Ansible Controller, also in
check mode, so a wrong file is reported before anything is copied. The archive
is about 140 MB and is copied only when the installed binary has a different
version than :envvar:`vmagent__version`.

Hosts with different architectures need separate archives; the
:envvar:`vmagent__release_archive_name` variable contains the architecture of
the host and can be used to select the right one:

.. code-block:: yaml

   vmagent__controller_archive_path: '/srv/archives/{{ vmagent__release_archive_name }}'


Binary in the host image
------------------------

When the image build already includes the binary at
:envvar:`vmagent__bin_path`, disable its installation:

.. code-block:: yaml

   vmagent__skip_install: True

The role still manages the configuration, the systemd unit and the instances.


Changing the version
--------------------

When you change :envvar:`vmagent__version`, update the checksums in
:envvar:`vmagent__archive_sha256_map` as well. The GitHub Releases API
publishes them in the ``digest`` field of the release assets:

.. code-block:: none

   $ curl -fsSL https://api.github.com/repos/VictoriaMetrics/VictoriaMetrics/releases/tags/v1.156.0 \
       | jq -r '.assets[] | select(.name | test("^vmutils-linux-(amd64|arm64)-v[0-9.]+\\.tar\\.gz$"))
                          | "\(.name) \(.digest)"'

Without access to the API, compute the checksums of the archives you copied
with the :command:`sha256sum` command, after checking them against the
``*_checksums.txt`` files published next to the archives:

.. code-block:: yaml

   vmagent__version: '1.156.0'
   vmagent__archive_sha256_map:
     'amd64': 'd71f7f00e07782531000620ec6c2a9d7ec83324f364dd1f36095ab378b5fb43b'
     'arm64': '1a8e4ed55df2a59d5cd03056213f50d293d4fab029e38dd960597362d92cf176'

Update the archives on the mirror or the Ansible Controller at the same time,
otherwise the installation of the new version fails.
