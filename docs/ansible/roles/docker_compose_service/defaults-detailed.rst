.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.docker_compose_service`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _docker_compose_service__ref_services:

docker_compose_service__services
--------------------------------

The ``docker_compose_service__*_services`` variables define Docker Compose
projects managed by this role. The variables are lists of YAML dictionaries,
each dictionary defines a Compose project. Entries from multiple lists are
merged together in order: ``default``, all hosts, group, host.

Examples
~~~~~~~~

Minimal service definition (``name`` and ``compose_src`` are required):

.. code-block:: yaml

   docker_compose_service__host_services:

     - name: 'myapp'
       compose_src: 'docker_compose_service/myapp/docker-compose.yml'

Service with environment variables and :command:`nginx` reverse proxy:

.. code-block:: yaml

   docker_compose_service__host_services:

     - name: 'immich'
       compose_src: 'docker_compose_service/immich/docker-compose.yml'
       env:
         UPLOAD_LOCATION: '/mnt/photo'
         DB_PASSWORD: '{{ lookup("password", secret
                          + "/docker_compose_service/immich/db_password
                             chars=ascii_letters,digits length=32") }}'
         IMMICH_VERSION: 'release'
       nginx:
         enabled: true
         fqdn: 'immich.example.com'
         port: '2283'
         proxy_options: |
           proxy_buffering off;
           client_max_body_size 50G;
           proxy_read_timeout 600s;
           proxy_send_timeout 600s;
           send_timeout 600s;

Service with inline Compose content (no template file needed):

.. code-block:: yaml

   docker_compose_service__host_services:

     - name: 'whoami'
       compose_content: |
         services:
           whoami:
             image: traefik/whoami:latest
             ports:
               - '127.0.0.1:8080:80'
             restart: unless-stopped
       nginx:
         enabled: true
         fqdn: 'whoami.example.com'
         port: '8080'

Service with additional Compose files (e.g. hardware acceleration overlay):

.. code-block:: yaml

   docker_compose_service__host_services:

     - name: 'immich'
       compose_src: 'docker_compose_service/immich/docker-compose.yml'
       compose_files:
         - src: 'docker_compose_service/immich/hwaccel.ml.yml'
           dest: 'hwaccel.ml.yml'
       env:
         IMMICH_VERSION: 'release'

Removing a previously deployed project:

.. code-block:: yaml

   docker_compose_service__host_services:

     - name: 'old-project'
       state: 'absent'

Syntax
~~~~~~

Each entry in the services list is a YAML dictionary with the following
parameters:

``name``
  Required. Name of the Docker Compose project. Used as the project directory
  name under :envvar:`docker_compose_service__data_path` (unless
  ``compose_dir`` is specified), the :command:`nginx` configuration filename,
  and an identifier in role tasks. Must be unique across all service lists.

``state``
  Optional. Defines the desired state of the Compose project. Supported
  values:

  - ``present`` (default): project is created and brought up
  - ``stopped``: project exists but all containers are stopped
  - ``absent``: project is removed (``docker compose down``)
  - ``ignore``: entry is skipped entirely (DebOps convention)

``compose_dir``
  Optional, string. Absolute path to the Docker Compose project directory
  on the host. Defaults to
  ``{{ docker_compose_service__data_path }}/<name>``.
  The directory is created automatically.

``compose_src``
  Optional, string. Path to a Jinja2 template file for the
  ``docker-compose.yml``, relative to the Ansible ``templates/`` search path.
  Mutually exclusive with ``compose_content``. One of ``compose_src`` or
  ``compose_content`` must be provided when ``state`` is ``present``.

  Template files are typically placed in the DebOps resources directory::

      ansible/resources/templates/by-host/<hostname>/
        docker_compose_service/<name>/docker-compose.yml

``compose_content``
  Optional, string. Inline content for the ``docker-compose.yml`` file.
  Mutually exclusive with ``compose_src``. Useful for simple projects that
  don't need a separate template file.

``compose_files``
  Optional, list of dictionaries. Additional Compose files to deploy into
  the project directory (e.g. hardware acceleration overlays). Each entry has:

  ``src``
    Required, string. Path to a Jinja2 template, relative to the Ansible
    ``templates/`` search path.

  ``dest``
    Optional, string. Destination filename within the project directory.
    Defaults to the basename of ``src``.

``env``
  Optional, dictionary. Environment variables written to the ``.env`` file
  in the project directory. Keys are variable names, values are strings.
  Sensitive values such as passwords can be auto-generated using the
  ``lookup("password", secret + "/docker_compose_service/<name>/...")``
  pattern. Mutually exclusive with ``env_file_src``.

``env_file_src``
  Optional, string. Path to a Jinja2 template for the ``.env`` file,
  relative to the Ansible ``templates/`` search path. Use this instead of
  ``env`` when you need full control over the ``.env`` file format.
  Mutually exclusive with ``env``.

``pull``
  Optional, boolean. Whether to run ``docker compose pull`` before bringing
  the project up. Defaults to :envvar:`docker_compose_service__pull`
  (``True``).

``remove_orphans``
  Optional, boolean. Whether to remove containers for services not defined
  in the Compose file. Defaults to ``True``.

``data_dirs``
  Optional, list of dictionaries. Directories to create on the host before
  the Compose project is started. Useful for pre-creating mount point
  subdirectories (e.g. on NFS volumes) with specific ownership and
  permissions that the containerized application expects. Each entry has:

  ``path``
    Required, string. Absolute path of the directory to create.

  ``owner``
    Optional, string. Directory owner (name or UID). By default not
    explicitly set (inherits from the parent directory).

  ``group``
    Optional, string. Directory group (name or GID). By default not
    explicitly set.

  ``mode``
    Optional, string. Directory permissions. Defaults to ``0755``.

``config_files``
  Optional, list of dictionaries. Configuration files to create on the host
  before bringing up the Compose project. Each entry creates a file that can
  be bind-mounted into containers via volumes defined in the Compose file.
  The Compose project is automatically recreated when a config file changes.
  Two modes are supported:

  ``dest``
    Required, string. Absolute path on the host where the file will be
    created. Parent directories are created automatically.

  ``content``
    Optional, string. Inline file content. Mutually exclusive with ``src``.
    Jinja2 expressions are evaluated at variable expansion time.

  ``src``
    Optional, string. Path to a Jinja2 template file, relative to the
    Ansible ``templates/`` search path. Mutually exclusive with ``content``.

  ``mode``
    Optional, string. File permissions. Defaults to ``0644``.

  ``owner``
    Optional, string. File owner. Defaults to ``root``.

  ``group``
    Optional, string. File group. Defaults to ``root``.

``config_dir``
  Optional, dictionary. A directory of template files to render on the host,
  useful for applications that need many configuration files. The directory
  tree is scanned using ``community.general.filetree`` and all files are
  rendered as Jinja2 templates. The Compose project is automatically
  recreated when any file changes.

  ``src``
    Required, string. Path to a directory of template files on the Ansible
    Controller. Relative paths are resolved against the ``templates/``
    search path. The directory structure is replicated under ``dest``.

  ``dest``
    Required, string. Absolute path on the host where the rendered files
    will be placed.

  ``mode``
    Optional, string. Default file permissions for rendered files. Defaults
    to ``0644``.

  ``owner``
    Optional, string. File owner. Defaults to ``root``.

  ``group``
    Optional, string. File group. Defaults to ``root``.

``nginx``
  Optional, dictionary. When present and ``enabled: true``, configures an
  :command:`nginx` reverse proxy virtual host for this service. See
  :ref:`docker_compose_service__ref_nginx` for details.


.. _docker_compose_service__ref_nginx:

docker_compose_service__services nginx parameters
--------------------------------------------------

The ``nginx`` dictionary within a service entry controls the :command:`nginx`
reverse proxy configuration. The role generates :command:`nginx` upstream and
server block definitions that are passed to the :ref:`debops.nginx` role.

The parameters are identical to those in the :ref:`debops.docker_service` role.

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
  server block. Defaults to ``<name>.<docker_compose_service__domain>``.

``port``
  Required (when ``enabled: true``), string. The host-side port that
  :command:`nginx` should proxy to. This must match the port exposed by the
  Compose service on ``127.0.0.1``.

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
