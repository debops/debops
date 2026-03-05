.. Copyright (C) 2024-2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2024-2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.docker_service`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _docker_service__ref_services:

docker_service__services
------------------------

The ``docker_service__*_services`` variables define Docker container services
managed by this role. The variables are lists of YAML dictionaries, each
dictionary defines a container service. Entries from multiple lists are merged
together in order: ``default``, all hosts, group, host.

Examples
~~~~~~~~

Minimal service definition (only ``name`` and ``image`` are required):

.. code-block:: yaml

   docker_service__host_services:

     - name: 'redis'
       image: 'redis:7-alpine'

Service with port mapping and persistent storage:

.. code-block:: yaml

   docker_service__host_services:

     - name: 'victoriametrics'
       image: 'victoriametrics/victoria-metrics:v1.93.0'
       ports:
         - '127.0.0.1:8428:8428'
       volumes:
         - '/srv/docker/victoriametrics/data:/victoria-metrics-data'
       command: '-retentionPeriod=12 -selfScrapeInterval=10s'
       nginx:
         enabled: true
         fqdn: 'vmetrics.example.com'
         port: '8428'

Service with environment variables and resource limits:

.. code-block:: yaml

   docker_service__host_services:

     - name: 'grafana'
       image: 'grafana/grafana:11.0.0'
       ports:
         - '127.0.0.1:3000:3000'
       volumes:
         - '/srv/docker/grafana/data:/var/lib/grafana'
       env:
         GF_SERVER_ROOT_URL: 'https://grafana.example.com'
       memory: '512m'
       cpus: 1.0
       nginx:
         enabled: true
         fqdn: 'grafana.example.com'
         port: '3000'
         proxy_options: |
           proxy_buffering off;

Removing a previously deployed service:

.. code-block:: yaml

   docker_service__host_services:

     - name: 'old-service'
       state: 'absent'

Syntax
~~~~~~

Each entry in the services list is a YAML dictionary with the following
parameters:

``name``
  Required. Name of the Docker container. Also used as an identifier when
  generating :command:`nginx` configuration filenames. Must be unique across
  all service lists.

``image``
  Required (unless ``state`` is ``absent``). Docker image to use for the
  container, including the tag (e.g. ``grafana/grafana:11.0.0``).

``state``
  Optional. Defines the desired state of the container service. Supported
  values:

  - ``present`` (default): container is created and started
  - ``stopped``: container exists but is not running
  - ``absent``: container is removed
  - ``ignore``: entry is skipped entirely (DebOps convention)

``restart_policy``
  Optional, string. Docker restart policy for the container. Defaults to
  the value of :envvar:`docker_service__restart_policy` (``unless-stopped``).
  Supported values: ``no``, ``always``, ``on-failure``, ``unless-stopped``.

``pull``
  Optional, boolean. Whether to pull the Docker image before managing the
  container. Defaults to :envvar:`docker_service__pull` (``True``).

``command``
  Optional, string or list. Override the default command (``CMD``) of the
  Docker image.

``entrypoint``
  Optional, list. Override the default entrypoint (``ENTRYPOINT``) of the
  Docker image.

``user``
  Optional, string. Username or UID to run the container process as.

``ports``
  Optional, list of strings. Port mappings in standard Docker format:
  ``[host_ip:]host_port:container_port[/protocol]``. For services behind an
  :command:`nginx` reverse proxy, bind to localhost only:
  ``127.0.0.1:8080:8080``.

``networks``
  Optional, list of dictionaries. Docker networks to connect the container to.
  Each entry must have a ``name`` key with the network name.

``dns``
  Optional, list of strings. Custom DNS servers for the container.

``hostname``
  Optional, string. Hostname to set inside the container.

``volumes``
  Optional, list of strings. Volume mounts in standard Docker format:
  ``host_path:container_path[:options]``. The role automatically creates host
  directories for bind mounts (paths starting with ``/``).

``tmpfs``
  Optional, list of strings. Tmpfs mounts inside the container.

``env``
  Optional, dictionary. Environment variables passed to the container.
  Keys are variable names, values are strings.

``memory``
  Optional, string. Memory limit for the container (e.g. ``512m``, ``1g``).

``memory_reservation``
  Optional, string. Soft memory limit for the container.

``cpus``
  Optional, number. CPU limit for the container (e.g. ``1.5`` for one and
  a half CPUs).

``capabilities``
  Optional, list of strings. Linux capabilities to add to the container
  (e.g. ``NET_ADMIN``).

``sysctls``
  Optional, dictionary. Sysctl settings for the container.

``read_only``
  Optional, boolean. If ``True``, the container filesystem is mounted
  read-only.

``labels``
  Optional, dictionary. Labels to apply to the container.

``healthcheck``
  Optional, dictionary. Container healthcheck configuration with the
  following keys: ``test`` (list), ``interval`` (string), ``timeout``
  (string), ``retries`` (integer), ``start_period`` (string).

``nginx``
  Optional, dictionary. When present and ``enabled: true``, configures an
  :command:`nginx` reverse proxy virtual host for this service. See
  :ref:`docker_service__ref_nginx` for details.


.. _docker_service__ref_nginx:

docker_service__services nginx parameters
-----------------------------------------

The ``nginx`` dictionary within a service entry controls the :command:`nginx`
reverse proxy configuration. The role generates :command:`nginx` upstream and
server block definitions that are passed to the :ref:`debops.nginx` role.

Examples
~~~~~~~~

Minimal :command:`nginx` configuration:

.. code-block:: yaml

   nginx:
     enabled: true
     fqdn: 'app.example.com'
     port: '8080'

Full :command:`nginx` configuration with all options:

.. code-block:: yaml

   nginx:
     enabled: true
     fqdn: 'app.example.com'
     port: '8080'
     type: 'proxy'
     proxy_headers: true
     proxy_options: |
       proxy_buffering off;
       proxy_read_timeout 300s;
     options: |
       client_max_body_size 50m;
     allow:
       - '192.168.1.0/24'
       - '10.0.0.0/8'
     deny_all: true
     auth_basic: true
     auth_basic_realm: 'Restricted'

Syntax
~~~~~~

``enabled``
  Required, boolean. If ``True``, an :command:`nginx` reverse proxy is
  configured for this service. If ``False`` or the ``nginx`` dictionary is
  absent, no proxy is created.

``fqdn``
  Optional, string. Fully Qualified Domain Name for the :command:`nginx`
  server block. Defaults to ``<name>.<docker_service__domain>``.

``port``
  Required (when ``enabled: true``), string. The host-side port that
  :command:`nginx` should proxy to. This must match the host port in the
  service ``ports`` mapping.

``type``
  Optional, string. The :command:`nginx` server template type. Defaults to
  ``proxy``. See :ref:`debops.nginx` documentation for other available types.

``proxy_headers``
  Optional, boolean. If ``True`` (default), standard proxy headers are
  included (``X-Real-IP``, ``X-Forwarded-For``, ``X-Forwarded-Proto``,
  ``Host``).

``proxy_options``
  Optional, YAML text block. Additional :command:`nginx` directives placed
  inside the ``location`` block, after the proxy headers.

``options``
  Optional, YAML text block. Additional :command:`nginx` directives placed
  inside the ``server`` block.

``allow``
  Optional, list of strings. IP addresses or CIDR networks allowed to access
  the service. When empty (default), no access restrictions are applied.

``deny_all``
  Optional, boolean. If ``True`` and ``allow`` is specified, a ``deny all``
  directive is added after the allow rules. Defaults to ``False``.

``ssl``
  Optional, boolean. Enable HTTPS through DebOps PKI. Defaults to ``True``
  (handled by the :ref:`debops.nginx` role defaults).

``auth_basic``
  Optional, boolean. Enable HTTP Basic Authentication. Defaults to ``False``.

``auth_basic_realm``
  Optional, string. The authentication realm displayed to users when
  ``auth_basic`` is enabled.
