Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

Docker is available in two editions. Community Edition (CE) and Enterprise Edition (EE).
Docker EE is not supported on Debian distributions. See also: `Docker variants`_.

The Docker package from distribution repositories will be installed by default
(on Jessie it means that the ``jessie-backports`` repository needs to be available,
which is the default in DebOps). You can install the upstream version of Docker
by setting the ``docker__upstream: True`` variable in Ansible’s inventory.
Upstream Docker is installed on Debian Stretch by default, since the this
release does not provide included Docker packages.

If :ref:`debops.pki` was configured on the host, Docker will automatically listen
on its TCP port for incoming TLS connections, which is by default blocked by
the :program:`ferm` firewall. If you don't use a firewall or have it disabled, you might
want to set :envvar:`docker__tcp` to ``False`` to disable this behavior.

Docker manages its own network bridge and :command:`iptables` entries. On hosts
that don't use upstream Docker packages, the :program:`ferment` Python script
will be installed in a Python virtualenv to allow :program:`ferm` firewall to
reload Docker firewall rules automatically, however it does not fully support
Docker yet, so be aware of this when you modify the firewall configuration.You
can restart :command:`docker` daemon to make sure that all firewall rules are
set up correctly.

On hosts with upstream Docker enabled and :command:`ferm`, a special post-hook
script will be installed that restarts the Docker daemon after :command:`ferm`
is restarted. In this case, :command:`ferment` will not be installed.

The :command:`docker-compose` script will be installed on hosts with upstream
Docker, in a Python virtualenv. It will be automatically available system-wide
via a symlink in :file:`/usr/local/bin/` directory.

To let the docker daemon trust a private registry with self-signed certificates,
add the root CA used to sign the registry's certificate through the :ref:`debops.pki`
role.

This role does not support switching from Docker CE to Docker EE on an already installed
machine. It does support switching from distribution repository to upstream.
However, it is recommended to start with a clean machine if possible.

``debops.docker`` relies on configuration managed by :ref:`debops.core`,
:ref:`debops.ferm`, and :ref:`debops.pki` Ansible roles.

.. _Docker variants: https://docs.docker.com/engine/installation/#docker-variants

Useful variables
----------------

This is a list of role variables which your most likely want to define in
Ansible inventory to customize Docker:

:envvar:`docker__tcp_allow`
  List of IP addresses or subnets that can connect to Docker daemon remotely
  over TLS.

:envvar:`docker__admins`
  List of UNIX accounts that have access to Docker daemon socket.

Example inventory
-----------------

To configure Docker on a given remote host, it needs to be added to
``[debops_service_docker]`` Ansible inventory group:

.. code-block:: none

   [debops_service_docker]
   hostname

Example playbook
----------------

Here's an example playbook that can be used to manage Docker:

.. literalinclude:: ../../../../ansible/playbooks/service/docker.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::docker``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::docker:config``
  Run tasks related to Docker configuration.

``role::docker:admins``
  Manage access to Docker daemon by UNIX accounts.
