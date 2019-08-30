Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:

The ``debops.tinc`` role by itself only defines the connections between hosts,
posing as Ethernet tunnels. To make a proper network, you need a defined
subnet and a way to assign IP addresses to hosts in the network. You can use
the :ref:`debops.ifupdown` role to define an internal subnet for the hosts in
the VPN, and :ref:`debops.dnsmasq` to provide DHCP and DNS services inside the
network.

Example inventory
-----------------

Hosts added to the ``[debops_service_tinc]`` inventory group will have the
``tinc`` daemon installed and configured.

Here is a example inventory that defines a Tinc ``mesh0`` VPN with one of the
hosts acting as the DHCP/DNS server and optionally a gateway:

.. code-block:: none

   [debops_service_ifupdown]
   gateway

   [debops_service_dnsmasq]
   gateway

   [debops_service_tinc]
   gateway
   hostname1
   hostname2

If you don't want the hosts to be included by default in any Tinc mesh
networks, you can put them in the ``[debops_service_tinc_aux]`` inventory group
instead.

The ``gateway`` needs some additional configuration which should be placed in
the Ansible inventory of the host:

.. code-block:: yaml

   tinc__host_networks:
     'mesh0':
       bridge: 'br2'

   ifupdown__host_interfaces:
     'br2':
       type: 'bridge'
       inet: 'static'
       inet6: 'static'
       nat: True
       addresses:
         - '2001:db8::23/64'
         - '192.0.2.23/24'

By default Tinc configures host configuration to contain the primary FQDN address
of a given host, so that when its IP address changes, Tinc will query the DNS
to get the current IP address. In addition, all publicly routable IP addresses
will be added to the host configuration file as well.

However, the FQDN will only be added, if a given host has a publicly routable
IP address. This means that hosts without public IPs won't have their addresses
mentioned in their host configuration file. This allows these hosts to still connect
to a public gateway with access to the Tinc network.

If you want to test the Tinc VPN only on a private network, or allow VPN
connections between hosts, you can tell the ``debops.tinc`` role to add the
private IP addresses of the hosts to their host configuration files by adding
in the Ansible inventory:

.. code-block:: yaml

   tinc__host_addresses: '{{ tinc__host_addresses_fqdn +
                             tinc__host_addresses_ip_public +
                             tinc__host_addresses_ip_private }}'

Example playbook
----------------

The ``debops.tinc`` role uses other roles present in the DebOps project to
configure certain aspects of a host, like firewall, installation of the
``tinc`` package from Debian Backports repository on certain OS releases, and
so on. To do that, a special Ansible playbook is used to access other roles.
A "mini role" called ``debops.tinc/env`` is used to pass variable data
generated from templates to other roles.

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.tinc`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/tinc-plain.yml
   :language: yaml

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.tinc`` together with the :ref:`debops.persistent_paths`:

.. literalinclude:: ../../../../ansible/playbooks/service/tinc-persistent_paths.yml
   :language: yaml

Static vs DHCP connection type
------------------------------

By default, the ``debops.tinc`` role configures a node to start its VPN interface
in a "DHCP" mode, without connecting to any other bridge interface, and ask the
mesh network for an IP address.

To have properly configured networking in the mesh, you need to configure at
least one VPN host to work in a "static" mode and preferably connect it to
a bridge which connects to a network with DHCP/DNS server. If the ``bridge``
parameter is specified without the ``link_type``, role will assume that the
host should be configured as ``static`` and enable this automatically.

Example network configuration:

.. code-block:: yaml

   tinc__host_networks:
     'mesh0':
       link_type: 'static'
       bridge: 'br2'

In this mode, hosts will be configured to start their VPN interface with a
dummy ``0.0.0.0`` IP address and connect it to a specified bridge.
This bridge can be created by the :ref:`debops.ifupdown`.

In "static" mode, the VPN interface will act as another layer 2 connection on
the bridge and DHCP requests from the VPN will be passed along to a suitable
server. You can configure a DHCP/DNS server using :ref:`debops.dnsmasq`.

Host configuration exchange
---------------------------

The ``debops.tinc`` role uses directories created in the :file:`secret/tinc/`
directory on the Ansible Controller to exchange host configuration files which
contain the RSA public keys between hosts in a given VPN. Each network has its
own directory tree:

.. code-block:: none

    secret/tinc/
    └── networks/
        └── mesh0/
            ├── by-group/
            │   ├── all/
            │   │   └── hosts/
            │   └── debops_service_tinc_mesh0/
            │       └── hosts/
            ├── by-host/
            │   ├── gateway/
            │   │   └── hosts/
            │   ├── hostname1/
            │   │   └── hosts/
            │   └── hostname/
            │       └── hosts/
            └── by-network/
                └── mesh0/
                    └── hosts/
                        ├── gateway
                        ├── hostname1
                        └── hostname2

By default all host configuration files in a given mesh network will be stored in::

    secret/tinc/networks/<mesh>/by-network/<mesh>/hosts/

The :file:`by-group/all/hosts/` directory can be used to distribute public keys to
all hosts in a given mesh network. You can also distribute the keys only to
hosts in a particular Ansible group, or even to a specific host.

Only the hosts in the current :command:`ansible-playbook` run will get the keys
present in the :file:`hosts/` directories. This means that when you add a new host
to the mesh, you will need to run the role against all of the hosts of the
mesh, otherwise the new host won't be accepted by the mesh due to unknown
public keys.

Support for systemd tinc@.service instances
-------------------------------------------

On a legacy systems without ``systemd``, you can manage Tinc VPN networks using
the :file:`/etc/init.d/tinc` init script.

If ``systemd`` is detected as the current init process, ``debops.tinc`` will
configure a set of ``systemd`` unit files:

``tinc.service``
  This is the main unit that manages all of the Tinc VPN networks and
  propagates start/stop/restart events.

``tinc@.service``
  This unit can be used to manage individual Tinc networks. The unit argument
  is the name of the VPN.

With ``systemd``, you can manage each Tinc network separately by issuing
commands:

.. code-block:: console

    systemctl status tinc@mesh0
    systemctl start tinc@mesh0
    systemctl stop tinc@mesh0

:ref:`debops.persistent_paths` support
--------------------------------------

In case the host in question happens to be a TemplateBasedVM on `Qubes OS`_ or
another system where persistence is not the default, it should be absent in
``debops_service_tinc`` and instead be added to the
``debops_service_tinc_persistent_paths`` Ansible inventory group
so that the changes can be made persistent:

.. code:: ini

   [debops_service_tinc_persistent_paths]
   hostname

Note that the :envvar:`tinc__user` (``tinc-vpn`` by default) created by the
role is not made persistent because making :file:`/etc/passwd` and related
files persistent might interfere with template changes.

You will need to ensure that the user exists by one of the following ways:

* Create the user in the template using :command:`useradd --system tinc-vpn --comment 'tinc VPN service' --home-dir '/etc/tinc' --shell '/bin/false'`
* Running the above command on start in the TemplateBasedVM
* Run the role against your template with the role configured in such a way
  that it only creates the user.
  Note that this is normally `discouraged on Qubes OS <https://www.qubes-os.org/doc/software-update-vm/#notes-on-trusting-your-templatevms>`_.

Besides that, the :envvar:`tinc__base_packages` are expected to be present (typically installed in the TemplateVM).

Also note that you will need to set ``core__unsafe_writes`` to ``True`` when you
attempt to update the configuration on a system that uses bind mounts for
persistence. You can set ``core__unsafe_writes`` directly in your inventory
without the need to run the ``debops.core`` role for this special case.
Refer to `Templating or updating persistent files`_ for details.

.. _Templating or updating persistent files: https://docs.debops.org/en/latest/ansible/roles/debops.persistent_paths/guides.html#templating-or-updating-persistent-files
