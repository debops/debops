.. Copyright (C) 2015-2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019      Imre Jonk <mail@imrejonk.nl>
.. Copyright (C) 2015-2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:

Initial configuration
---------------------

By default Docker is installed from Debian repositories. Users can enable
upstream Docker APT repositories using the :envvar:`docker_server__upstream`
boolean variable. When it's set to ``True``, the :ref:`debops.extrepo` Ansible
role will be used to configure the repository. Upstream and Debian versions can
be downgraded and upgraded as needed, but the role doesn't remove packages that
are no longer needed by either version.

The :command:`docker-compose` command doesn't exist when upstream Docker is
installed. Users can use the :command:`docker compose` subcommand instead,
since Compose is implemented as a Go plugin.

The role can configure :command:`systemd-resolved` service on the host to
listen for DNS queries on the ``docker0`` interface. This way, Docker
containers can utilize the host's DNS resolver to resolve hostnames and FQDNs.
This works with the default network configuration used by Docker.

The role can configure the firewall (via the :ref:`debops.ferm` role) to allow
connections to ports used in `Docker Swarm`__ mode; this is disabled by
default. Currently, Swarm setup is not implemented and needs to be performed
manually.

.. __: https://docs.docker.com/engine/swarm/admin_guide/


.. _docker_server__ref_systemd:

Docker and :command:`systemd` integration
-----------------------------------------

Some of the Docker configuration options need to be configured via
:command:`systemd` units, to override command line arguments (for example the
``-H`` or ``--host`` option cannot be modified using the daemon configuration
file) or define environment variables for the daemon (for example HTTP/HTTPS
proxy which should be used to access external sites). This can be done using
the :ref:`debops.systemd` Ansible role, which is included in the
:file:`service/docker_server.yml` playbook.

The :envvar:`docker_server__systemd__dependent_units` variable can be used to
add :command:`systemd` configuration which will be applied to the host when the
Docker service is configured. For example, to add HTTP proxy configuration,
define this in the Ansible inventory:

.. code-block:: yaml

   docker_server__systemd__dependent_units:

     - name: 'docker.service.d/proxy.conf'
       comment: 'Proxy configuration for Docker'
       raw: |
         [Service]
         Environment="http_proxy=http://proxy.example.com:3128"
         Environment="https_proxy=http://proxy.example.com:3128"
         Environment="no_proxy=localhost,127.0.0.1,docker-registry.example.com,.corp"
       state: 'present'
       restart: 'docker.service'

This will add the :file:`/etc/systemd/system/docker.service.d/proxy.conf` unit
on the host and restart the :file:`docker.service` unit after the playbook is
finished.


Example inventory
-----------------

To configure Docker on a given remote host, it needs to be added to the
``[debops_service_docker_server]`` Ansible inventory group:

.. code-block:: none

   [debops_service_docker_server]
   hostname


Example playbook
----------------

Here's an example playbook that can be used to manage Docker:

.. literalinclude:: ../../../../ansible/playbooks/service/docker_server.yml
   :language: yaml
   :lines: 1,6-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::docker_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::docker_server:config``
  Run tasks related to Docker configuration.

``role::docker_server:admins``
  Manage access to Docker daemon by UNIX accounts.


Other resources
---------------

List of other useful resources related to the ``debops.docker_server`` Ansible
role:

- Manual pages: :man:`docker(1)`, :man:`docker-run(1)`, :man:`Dockerfile(5)`,
  :man:`docker-compose(1)`

- `Docker`__ page on Debian Wiki

  .. __: https://wiki.debian.org/Docker

- `Docker`__ page on Arch Linux Wiki

  .. __: https://wiki.archlinux.org/index.php/Docker

- `Docker documentation page`__

  .. __: https://docs.docker.com/

- `Docker guide for Ansible`__

  .. __: https://docs.ansible.com/ansible/latest/scenario_guides/guide_docker.html

- Official DebOps image in the Docker Hub: `debops/debops`__ (see also
  :ref:`quick_start__docker`)

  .. __: https://hub.docker.com/r/debops/debops
