Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

The Docker package from distribution repositories will be installed by default
(on Jessie it means that the ``jessie-backports`` repository needs to be available,
which is the default in DebOps). You can install the upstream version of Docker
by setting the ``docker__upstream: True`` variable in Ansible’s inventory.

If ``debops.pki`` was configured on the host, Docker will automatically listen
on its TCP port for incoming TLS connections, which is by default blocked by
the ``ferm`` firewall. If you don't use a firewall or have it disabled, you might
want to set ``docker__tcp`` to ``False`` to disable this behavior.

Docker manages its own network bridge and :command:`iptables` entries. The :program:`ferment`
Python script will be installed to allow ``ferm`` firewall to reload Docker
firewall rules automatically, however it does not fully support Docker yet, so
be aware of this when you modify the firewall configuration. You can restart
``docker`` daemon to make sure that all firewall rules are set up correctly.

To let the docker daemon trust a private registry with self-signed certificates,
add the root CA used to sign the registry's certificate through the ``debops.pki``
role.

``debops.docker`` relies on configuration managed by ``debops.core``,
``debops.ferm``, and ``debops.pki`` Ansible roles.

Useful variables
----------------

This is a list of role variables which your most likely want to define in
Ansible inventory to customize Docker:

``docker__tcp_allow``
  List of IP addresses or subnets that can connect to Docker daemon remotely
  over TLS.

``docker__admins``
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

.. literalinclude:: playbooks/docker.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::docker``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::docker:config``
  Run tasks related to Docker configuration.

``role::docker:admins``
  Manage access to Docker daemon by UNIX accounts.
