Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

Docker is available in two editions. Community Edition (CE) and Enterprise
Edition (EE). Docker EE is not supported on Debian distributions. See also:
`Docker variants`_.

The Docker package from distribution repositories will be installed by default
(on Jessie it means that the ``jessie-backports`` repository needs to be
available, which is the default in DebOps). You can install the upstream
version of Docker by setting the ``docker_server__upstream: True`` variable in
Ansible’s inventory. Upstream Docker is installed on Debian Stretch by default,
since this release does not provide included Docker packages.

A Docker server managed by DebOps does not listen on any TCP ports by default.
You can set :envvar:`docker_server__tcp` to ``True`` if you need remote access
to the Docker server. You will also need to tweak your firewall in this case,
which is easily done with :envvar:`docker_server__tcp_allow`. It is recommended
to use the :ref:`debops.pki` role to secure the connection between the client
and the Docker server.

On hosts with :command:`ferm` firewall support enabled, a special post-hook
script will be installed that restarts the Docker daemon after :command:`ferm`
is restarted.

The :command:`docker-compose` script will be installed on hosts with upstream
Docker, in a Python virtualenv. It will be automatically available system-wide
via a symlink in :file:`/usr/local/bin/` directory.

To let the docker daemon trust a private registry with self-signed
certificates, add the root CA used to sign the registry's certificate through
the :ref:`debops.pki` role.

This role does not support switching from Docker CE to Docker EE on an already
installed machine. It does support switching from distribution repository to
upstream. However, it is recommended to start with a clean machine if possible.

The :ref:`debops.docker_server` role relies on configuration managed by
:ref:`debops.core`, :ref:`debops.ferm`, and :ref:`debops.pki` Ansible roles.

.. _Docker variants: https://docs.docker.com/install/overview/


Useful variables
----------------

This is a list of role variables which you most likely want to define in
Ansible inventory to customize Docker:

:envvar:`docker_server__tcp`
  Enable or disable listening for TLS connections on the Docker TCP port.

:envvar:`docker_server__tcp_allow`
  List of IP addresses or subnets that can connect to Docker daemon remotely
  over TLS.

:envvar:`docker_server__admins`
  List of UNIX accounts that have access to Docker daemon socket.


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
