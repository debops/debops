.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _garage__ref_defaults_detailed:

Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.garage`` default variables have more extensive
configuration than simple strings or lists, here you can find
documentation and examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _garage__ref_configuration:

garage__configuration
---------------------

The ``garage__*_configuration`` variables define the contents of the
:file:`/etc/garage.toml` configuration file. The role uses the
:ref:`universal_configuration` system: the configuration is a list of YAML
dictionaries, which are merged into one dictionary and converted to TOML.
Any option from the `Garage configuration reference`__ can be set this way,
including tables like ``[s3_api]`` and arrays like a ``data_dir`` with
several disks. The generated file does not keep comments.

.. __: https://garagehq.deuxfleurs.fr/documentation/reference-manual/configuration/

The default configuration is defined in the
:envvar:`garage__default_configuration` variable. It uses the network and
cluster parameters of the role, for example :envvar:`garage__s3_port` and
:envvar:`garage__replication_factor`, which are also used by other roles
in the playbook. Change these values with the role variables, not in the
configuration lists. The role checks that ``replication_factor`` in the
final configuration is equal to :envvar:`garage__replication_factor`.

Syntax
~~~~~~

Each entry of the list is a YAML dictionary with specific parameters:

``name``
  Required. Name of the configuration entry, not used in the configuration
  file. An entry with the same name as an earlier entry replaces it, together
  with its whole ``config`` dictionary. Entries with different names are
  merged.

``config``
  Required. YAML dictionary with Garage configuration options. The ``config``
  dictionaries of all entries are merged recursively in the order of the
  entries, so an entry can add options to a table defined by an earlier
  entry. Lists are not merged, a later list replaces an earlier one.

``state``
  Optional. If not specified or ``present``, the entry is included in the
  configuration file. If ``absent``, the entry is not included, which removes
  an entry with the same name defined earlier. If ``ignore``, the entry is
  not evaluated by the role.

Examples
~~~~~~~~

Store object data on several disks, as shown in the upstream
`real-world deployment guide`__. The entry replaces the default
``data_dir`` entry; the role creates the listed directories and allows the
daemon to write to them:

.. __: https://garagehq.deuxfleurs.fr/documentation/cookbook/real-world/

.. code-block:: yaml

   garage__host_configuration:

     - name: 'data_dir'
       config:
         data_dir:
           - path: '/srv/garage/hdd1'
             capacity: '2T'
           - path: '/srv/garage/hdd2'
             capacity: '4T'

Add options to the existing tables, for example the public endpoint used
in presigned URLs behind a reverse proxy and the index document of
websites:

.. code-block:: yaml

   garage__configuration:

     - name: 'public_endpoints'
       config:
         s3_api:
           public_endpoint: 'https://s3.example.com'
         s3_web:
           index: 'index.html'

Set top-level options which the role does not define, and turn off the
automatic metadata snapshots:

.. code-block:: yaml

   garage__configuration:

     - name: 'compression'
       config:
         compression_level: 2

     - name: 'metadata_auto_snapshot_interval'
       state: 'absent'


.. _garage__ref_binary_source:

Binary source
-------------

The role checks the following cases in order and stops at the first one
that applies:

#. ``garage__skip_install: True`` - the role does not touch
   :envvar:`garage__bin_path`. Useful when the binary is provided by
   a Packer-built image or an external package.

#. The binary at :envvar:`garage__bin_path` already reports the
   matching :envvar:`garage__version` (parsed from
   ``garage --version``). Nothing is copied or downloaded.

#. :envvar:`garage__controller_binary_path` is not empty. The role
   verifies the SHA256 checksum of that file on the Ansible Controller
   and copies it to :envvar:`garage__bin_path`.

#. Otherwise the role downloads :envvar:`garage__release_url` with
   :command:`ansible.builtin.get_url` to a temporary file next to
   :envvar:`garage__bin_path`. The download is verified against
   :envvar:`garage__binary_sha256` before it replaces the installed
   binary. The URL can point at an internal mirror, or use the
   ``file://`` scheme for a file which is already present on the host.

In both cases the new binary replaces the old one atomically, so the
running daemon is not stopped before the replacement; it is restarted
afterwards. When the installed version differs from
:envvar:`garage__version`, the upgrade gate documented in
:ref:`garage__ref_guide_upgrades` runs before any file is replaced.


.. _garage__ref_cluster_secrets:

Cluster-wide secrets
--------------------

``rpc_secret`` must be identical on every node. The role looks the
value up from:

:file:`secret/garage/clusters/{garage__cluster_name}/rpc_secret`

The path does not include ``inventory_hostname``. The admin token,
metrics token and the optional default access key use the same
directory. Changing :envvar:`garage__cluster_name` creates a new
secret namespace; nodes with different names will not form a cluster.

The role asserts that every host in :envvar:`garage__cluster_hosts`
uses the same :envvar:`garage__cluster_name` and
:envvar:`garage__replication_factor`.


.. _garage__ref_single_node:

Single-node bootstrap
---------------------

:envvar:`garage__single_node` defaults to ``True`` only when
:envvar:`garage__replication_factor` is ``1`` and
:envvar:`garage__cluster_hosts` contains only the current host. The
role requires Garage 2.3.0 or newer for this mode. The systemd unit then
starts Garage with ``--single-node``.

When :envvar:`garage__default_bucket` is non-empty, the unit also
gets ``--default-bucket`` and an ``EnvironmentFile`` with
``GARAGE_DEFAULT_ACCESS_KEY``, ``GARAGE_DEFAULT_SECRET_KEY`` and
``GARAGE_DEFAULT_BUCKET``. The daemon creates the bucket and key on
first start and refreshes their permissions on later starts. If a key
with the same id already exists with a different secret, Garage
refuses to start; the DebOps secret lookup keeps the values stable.

The role refuses to keep ``--single-node`` enabled when the local
fact ``ansible_local.garage.layout_version`` is greater than 1, so
that a later expansion cannot crash-loop the daemon.


.. _garage__ref_nginx_frontends:

nginx frontends
---------------

Garage has no native TLS. With :envvar:`garage__nginx_enabled`
(the default) the S3 API is published at
:envvar:`garage__nginx_s3_fqdn` plus the wildcard
``*.s3.<domain>`` for virtual-hosted bucket URLs. The proxy is
configured for large objects: ``client_max_body_size 0``,
``proxy_buffering off``, ``proxy_request_buffering off`` and
``proxy_max_temp_file_size 0``. The ``Host`` header is taken from
``$http_host`` so that path-style and virtual-hosted requests both
reach Garage intact.

Website hosting is a separate server, off by default. Set
:envvar:`garage__nginx_web_enabled` to ``True`` to publish
``*.web.<domain>``.

Without nginx, the S3 API and the website endpoint listen on loopback
and are reachable from other hosts only from the addresses listed in
:envvar:`garage__s3_allow` and :envvar:`garage__web_allow`. Both
endpoints then use plain HTTP, so list only the clients that need direct
access, or ``0.0.0.0/0`` and ``::/0`` for everyone.
