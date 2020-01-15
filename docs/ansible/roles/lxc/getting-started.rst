Getting started
===============

.. contents::
   :local:


LXC support in DebOps
---------------------

This role focuses only on the LXC configuration itself. You will need to use
other DebOps roles to manage additional required subsystems.

The role will configure an internal ``lxcbr0`` bridge for the local Linux
Containers, using the ``lxc-net`` service. The internal network will have its
own DHCP/DNS server with ``lxc.{{ ansible_domain }}`` DNS domain by default.
You can configure a DNS proxy on the LXC host to be able to access the LXC
containers by their DNS names instead of their IP addresses. The
:ref:`debops.dnsmasq` and :ref:`debops.unbound` Ansible roles will
automatically integrate with the LXC host configuration using Ansible local
facts and will generate the configuration necessary to access the
``lxc.{{ ansible_domain }}`` DNS domain.

Additional bridge network interfaces can be maintained using the
:ref:`debops.ifupdown` role. By default the :command:`ifupdown` role creates
the ``br0`` network bridge attached to the external network, which is defined
in the LXC configuration as the default network interface to attach the
containers, if the internal bridge is disabled.

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

The role will install the :command:`lxc-new-unprivileged` script which provides
an equivalent functionality to the above command. With it, you can create new
LXC unprivileged containers by running:

.. code-block:: console

   lxc-new-unprivileged <container>

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
be fairly secure, however you might want to consider enabling AppArmor for
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


LXC containers are managed by systemd
-------------------------------------

The LXC containers created by the role tasks or by the
:command:`lxc-new-unprivileged` script are managed by :command:`systemd`,
specifically by the ``lxc@.service`` unit. This is done because on Debian
Stretch using the :command:`lxc-stop` command directly to stop a container
results in a timeout and container processes being forcibly killed by the
system. On Debian Stretch and Ubuntu Xenial distributions, the
:command:`lxc@.service` :command:`systemd` unit is modified by the
:ref:`debops.lxc` role to shutdown the container "from the inside" via the
:command:`lxc-attach` command, which results in a properly shut down container.

The containers are configured to not start automatically by the ``lxc.service``
unit. Instead, each LXC container has its corresponding ``lxc@.service``
instance that will be started by :command:`systemd` on system boot. On
container destruction, either by the :ref:`debops.lxc` role or by the
:command:`lxc-destroy` command, the instance will be disabled automatically.

To start a LXC container using :command:`systemd` instances, you can issue the
command:

.. code-block:: console

   systemctl start lxc@<container>.service

To stop a running LXC container started by :command:`systemd`, you can execute
the command:

.. code-block:: console

   systemctl stop lxc@<container>.service

With this setup, you should avoid using the ``lxc-*`` commands that affect the
containers directly, unless the container started by the :command:`systemd` is
stopped first. Otherwise the state of the container managed by the
:command:`systemd` instance might get desynchronized.

References and more details about the issues:

- `Debian Bug #831691: Please use lxc.haltsignal = SIGRTMIN+3 for systemd containers`__

  .. __: https://bugs.debian.org/831691

- `[lxc-users] Graceful Shutdown/Reboot`__

  .. __: https://lists.linuxcontainers.org/pipermail/lxc-users/2017-February/012827.html

- `GitHub issue: Please use lxc.haltsignal = SIGRTMIN+3 for systemd containers`__

  .. __: https://github.com/lxc/lxc/issues/1085

- `GitHub issue: lxc stop does not stop my container`__

  .. __: https://github.com/lxc/lxd/issues/2947

- `Forum post: 'lxc-stop -n <container>' takes too long`__

  .. __: https://forum.turris.cz/t/lxc-stop-n-container-takes-too-long/6358


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

If :ref:`the LDAP support <debops.ldap>` is configured on a host and SSH key
lookup in LDAP is enabled by the :ref:`debops.sshd` role, the script will look
up the current user keys in LDAP directory as well - this ensures that the SSH
access is configured even when the SSH public keys are not explicitly defined
in the current user's :file:`~/.ssh/authorized_keys` file.

After that, the LXC container should be ready to be used remotely, at which
point you can use normal DebOps ``bootstrap`` playbook and other playbooks to
configure it.


Predictable MAC addresses
-------------------------

The :command:`lxc-hwaddr-static` script can be used to generate predictable,
randomized MAC addresses for LXC containers, based on the container name. The
script will automatically save the generated MAC addresses in the container
configuration files. Multiple network interfaces defined by the
``lxc.network.type`` configuration option are supported.

The script can also be used as a "pre-start" LXC hook, to configure static MAC
addresses at container start. This requires the container to be restarted for
the new static MAC addresses to be used in network interface setup. This usage
is enabled by default in DebOps via the common LXC container configuration.


Example inventory
-----------------

To enable LXC support on a host, it needs to be added to the
``[debops_service_lxc]`` Ansible inventory group:

.. code-block:: none

   [debops_all_hosts:children]
   lxc_hosts
   lxc_containers

   [debops_service_lxc:children]
   lxc_hosts

   [lxc_hosts]
   lxc-host    ansible_host=lxc-host.example.org

   [lxc_containers]
   webserver   ansible_host=webserver.example.org

By default, containers will use the ``lxcbr0`` bridge managed by the role, with
their own internal subdomain. You can use the :ref:`debops.ifupdown` Ansible
role to configure additional network bridges on the LXC host, if you want to
attach the containers to the public network.


Remote LXC management without SSH access
----------------------------------------

Remote LXC containers without SSH access can be accessed indirectly using the
`lxc_ssh`__ Ansible connection plugin included with DebOps. This requires
direct access to the ``root`` account on the LXC host and LXC container (even
with unprivileged LXC containers), due to the connection plugin limitations.

Example configuration of that connection in the Ansible inventory (variables
specified in multiple lines for readability):

.. code-block:: none

   [debops_all_hosts:children]
   lxc_hosts
   lxc_containers

   [debops_service_lxc:children]
   lxc_hosts

   [lxc_hosts]
   lxc-host    ansible_host=lxc-host.example.org

   [lxc_containers]
   webserver    ansible_connection=lxc_ssh ansible_user=root
   webserver    ansible_host=lxc-host.example.org
   webserver    ansible_ssh_extra_args=webserver

The ``lxc_ssh`` connection plugin is unofficial and may not work correctly.
Please report any issues, and if you know fixes for them, provide that as well!

.. __: https://github.com/andreasscherbaum/ansible-lxc-ssh


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

``role::lxc:containers``
  Execute tasks that manage LXC containers.

``role::lxc:net``
  Manage internal LXC network configuration.

``role::lxc:dnsmasq``
  Manage the :command:`dnsmasq` instance of the internal LXC network.


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
