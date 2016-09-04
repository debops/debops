Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst

The ``debops.tinc`` role by itself only defines the connections between hosts,
posing as Ethernet tunnels. To make a proper network, you need a defined
subnet and a way to assign IP addresses to hosts in the network. You can use
the debops.subnetwork_ role to define an internal subnet for the hosts in
the VPN, and debops.dnsmasq_ to provide DHCP and DNS services inside the
network.

Example inventory
-----------------

Hosts added to the ``[debops_service_tinc]`` inventory group will have the
``tinc`` daemon installed and configured.

Additionally, you need to add hosts to a separate inventory group defining
which hosts belong to a particular VPN mesh. For the default ``mesh0`` VPN, you
should use the ``[debops_service_tinc_mesh0]`` group.

Here is a example inventory that defines a Tinc ``mesh0`` VPN with one of the
hosts acting as the DHCP/DNS server and optionally a gateway:

.. code-block:: none

    [debops_service_subnetwork]
    gateway

    [debops_service_dnsmasq]
    gateway

    [debops_service_tinc:children]
    debops_service_tinc_mesh0

    [debops_service_tinc_mesh0]
    gateway   tinc__bridge_mesh0="br2" tinc__link_type_mesh0="static"
    hostname1
    hostname2

By default Tinc configures host configuration to contain the primary FQDN address
of a given host, so that when its IP address changes, Tinc will query the DNS
to get the current IP address.

However, the FQDN will only be added, if a given host has a publicly routable
IP address. This means that hosts without public IPs won't have their addresses
mentioned in their host configuration file. This allows these hosts to still connect
to public a gateway with access to the Tinc network.

If you want to test the Tinc VPN only on a private network, or allow VPN
connections between hosts, you can tell the ``debops.tinc`` role to add the
private IP addresses of the hosts to their host configuration files by adding
in the Ansible inventory:

.. code-block:: yaml

    tinc__host_addresses: '{{ tinc__host_addresses_ip }}'

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

.. literalinclude:: playbooks/tinc.yml
   :language: yaml

Static vs DHCP connection type
------------------------------

By default, the ``debops.tinc`` role configures a node to start its VPN interface
in a "DHCP" mode, without connecting to any other bridge interface, and ask the
mesh network for an IP address.

To have properly configured networking in the mesh, you need to configure at
least one VPN host to work in a "static" mode and preferably connect it to
a bridge which connects to a network with DHCP/DNS server:

.. code-block:: yaml

   tinc__network_dict:
     link_type: 'static'
     bridge: 'br2'

In this mode, hosts will be configured to start their VPN interface with a
dummy ``0.0.0.0`` IP address and connect it to a bridge, by default ``br2``.
This bridge can be created by the debops.subnetwork_ role, which defaults to
``br2`` as well.

In "static" mode, the VPN interface will act as another layer 2 connection on
the bridge and DHCP requests from the VPN will be passed along to a suitable
server. You can configure a DHCP/DNS server using debops.dnsmasq_ role.

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
