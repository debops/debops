Getting started
===============

.. contents::
   :local:


LXC support in DebOps
---------------------

This role focuses only on the LXC configuration itself. You will need to use
other DebOps roles to manage additional required subsystems.

Additional bridge network interfaces can be maintained using the
:ref:`debops.ifupdown` role. By default the :command:`ifupdown` role creates
the ``br0`` network bridge attached to the external network, which is defined
in the LXC configuration as the default network interface to attach the
containers.

The containers will use DHCP to get their network interface configuration.
You can use :ref:`debops.dnsmasq` or :ref:`debops.dhcpd` Ansible roles to
manage a DHCP service on the LXC host or elsewhere in the network.


Unprivileged containers
-----------------------

You can create unprivileged LXC container owned by the ``root`` account by
using the command:

.. code-block:: console

   lxc-create -n <container> -f /etc/lxc/unprivileged.conf \
              -t download -- --dist debian --release stretch --arch amd64

The container will be configured to use subordinate UID/GID range defined by
the :ref:`debops.root_account` Ansible role in the :file:`/etc/subuid` and
:file:`/etc/subgid` databases. Since it's a container owned by ``root``, it
will be automatically started on the boot of the host.

Multiple LXC containers that use the same set of subUIDs/subGIDs might be able
to access each others' resources in the case of a breakout, since from the
perspective of the host their UIDs/GIDs are the same. You might want to
consider this in the planning of your environment and use multiple
subUID/subGID ranges for different LXC containers or groups of them.

Currently unprivileged LXC containers managed in the DebOps environment should
be fairly secure, owever you might want to consider enabling AppArmor for
increased security against attacks directed at the LXC host.


Privileged containers
---------------------

You can create a privileged LXC container (default) by using the command as the
``root`` account:

.. code-block:: console

   lxc-create -n <container> -t debian

To select a different release, use this command:

.. code-block:: console

   lxc-create -n <container> -t debian -- -r jessie

You can also specify a different default configuration file, to for example
connect the container to specific network bridge:

.. code-block:: console

   lxc-create -n <container> -t debian -f /etc/lxc/privileged.conf

Remember that privileged LXC containers are not secure and can modify the LXC
host configuration. Don't use privileged containers in production environments,
and don't allow untrusted users access to the ``root`` account inside of these
containers.

The default configuration defined by the role is pretty simple, you can find
the configuration of each created LXC container in the
:file:`/var/lib/lxc/<container>/config` configuration file.


SSH access to containers
------------------------

You can use the command below to start an existing LXC container and prepare
SSH access to the ``root`` account:

.. code-block:: console

   lxc-prepare-ssh <container> [authorized_keys file]

The :command:`lxc-prepare-ssh` is a custom script installed by the
:ref:`debops.lxc` role. It will start the specified container, make sure that
OpenSSH service is installed inside, and add the current user's
:file:`~/.ssh/authorized_keys` contents on the ``root`` account inside of the
container. The script will check if the ``${SUDO_USER}`` variable is defined in
the environment and use that user's :file:`~/.ssh/authorized_keys` file as
source of SSH public keys. Alternatively, you can specify a custom file with
authorized SSH keys to add in the container's
:file:`/root/.ssh/authorized_keys` file.

After that, the LXC container should be ready to be used remotely, at which
point you can use normal DebOps ``bootstrap`` playbook and other playbooks to
configure it.


Example inventory
-----------------

To enable LXC support on a host, it needs to be added to the
``[debops_service_lxc]`` Ansible inventory group:

.. code-block:: none

   [debops_service_lxc]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.lxc`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/lxc.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::lxc``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.lxc`` Ansible role:

- Manual pages: :man:`lxc(7)`, :man:`lxc.conf(5)`, :man:`lxc.system.conf(5)`,
  :man:`lxc.container.conf(5)`

- `LXC`__ page in Debian Wiki

  .. __: https://wiki.debian.org/LXC

- `Linux Containers`__ page in Arch Linux Wiki

  .. __: https://wiki.archlinux.org/index.php/Linux_Containers

- `LXC 1.0 blog post series`__ written by Stéphane Graber

  .. __: https://stgraber.org/2013/12/20/lxc-1-0-blog-post-series/
