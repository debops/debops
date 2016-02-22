Getting started
===============

.. contents::
   :local:

``debops.tinc`` role by itself only defines the connections between hosts,
posing as Ethernet tunnels. To make the proper network, you need a defined
subnet and a way to assign IP addresses to hosts in the network. You can use
``debops.subnetwork`` role to define an internal subnet for the hosts in the
VPN, and ``debops.dnsmasq`` to provide DHCP and DNS services inside the
network.

Example inventory
-----------------

Hosts added in ``[debops_service_tinc]`` inventory group will have the ``tinc``
daemon installed and configured.

Additionally, you need to add hosts to a separate inventory group which defines
which hosts belong in a particular VPN mesh. For the default ``mesh0`` VPN, you
should use the ``[debops_service_tinc_mesh0]`` group.

Here's example inventory that defines a Tinc ``mesh0`` VPN with one of the
hosts acting as the DHCP/DNS server and optionally a gateway::

    [debops_service_subnetwork]
    gateway

    [debops_service_dnsmasq]
    gateway

    [debops_service_tinc:children]
    debops_service_tinc_mesh0

    [debops_service_tinc_mesh0]
    gateway   tinc_bridge_mesh0="br2" tinc_link_type_mesh0="static"
    hostname1
    hostname2

By default Tinc configures host public keys to contain the primary FQDN address
of a given host, so that when its IP address changes, Tinc will interrogate the
DNS to get the current IP address.

However, the FQDN will only be added, if a given host has a publicly routable
IP address. This means that hosts without public IPs won't have their addresses
mentioned in their public key files. This allows these hosts to still connect
to public gateway with access to the Tinc network.

If you want to test the Tinc VPN only on a private network, or allow VPN
connections between hosts, you can tell the ``debops.tinc`` role to add the
private IP addresses of the hosts to their public key files by adding in the
Ansible inventory::

    tinc_host_addresses: '{{ tinc_host_addresses_ip }}'

Example playbook
----------------

The ``debops.tinc`` role uses other roles present in the DebOps project to
configure certain aspects of a host, like firewall, installation of the
``tinc`` package from Debian Backports repository on certain OS releases, and
so on. To do that, a special Ansible playbook is used to access other roles.
A "mini role" called ``debops.tinc/env`` is used to pass variable data
generated from templates to other roles.

Here's an example playbook which uses ``debops.tinc`` role::

    ---

    - name: Configure tinc VPN
      hosts: [ 'debops_service_tinc' ]
      become: True

      roles:

        - role: debops.tinc/env
          tags: [ 'role::tinc', 'role::tinc:secret', 'role::secret', 'role::ferm', 'role::ifupdown' ]

        - role: debops.secret
          tags: [ 'role::secret', 'role::tinc:secret' ]
          secret_directories: '{{ tinc_env_secret_directories }}'

        - role: debops.apt_preferences
          tags: [ 'role::apt_preferences' ]
          apt_preferences_dependent_list: '{{ tinc__apt_preferences__dependent_list }}'

        - role: debops.etc_services
          tags: [ 'role::etc_services' ]
          etc_services_dependent_list: '{{ tinc_etc_services_dependent_list }}'

        - role: debops.ferm
          tags: [ 'role::ferm' ]
          ferm_dependent_rules: '{{ tinc_env_ferm_dependent_rules }}'

        - role: debops.tinc
          tags: [ 'role::tinc' ]

Static vs DHCP connection type
------------------------------

By default, ``debops.tinc`` role configures a node to start its VPN interface
in a "DHCP" mode, without connecting to any other bridge interface, and ask the
mesh network for an IP address.

To have properly configured networking in the mesh, you need to configure at
least one VPN host to work in a "static" mode and preferably connect it to
a bridge which connects to a network with DHCP/DNS server:

.. code-block:: yaml

   tinc_network_dict:
     link_type: 'static'
     bridge: 'br2'

In this mode, host will be configured to start the VPN interface with a dummy
``0.0.0.0`` IP address and connect it to a bridge, by default ``br2``. This
bridge can be created by ``debops.subnetwork`` role, which defaults to ``br2``
as well.

In the "static" mode, VPN interface will act as another Layer 2 connection on
the bridge and DHCP requests from the VPN will be passed along to a suitable
server. You can configure a DHCP/DNS server using ``debops.dnsmasq`` role.

RSA public key exchange
-----------------------

The ``debops.tinc`` role uses directories created in the ``secret/tinc/``
directory on Ansible Controller to exchange RSA public keys between hosts in
a given VPN. Each network has its own directory tree::

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

By default all public keys in a given mesh network will be stored in::

    secret/tinc/networks/<mesh>/by-network/<mesh>/hosts/

The ``by-group/all/hosts/`` directory can be used to distribute public keys to
all hosts in a given mesh network. You can also distirbute the keys only to
hosts in a particular Ansible group, or even to a specific host.

Only the hosts in the current ``ansible-playbook`` run will get the keys
present in the ``hosts/`` directories. This means that when you add a new host
to the mesh, you will need to run the role on all the hosts that you want to
have connections with, otherwise the new host won't be accepted by the mesh due
to uknown public keys.

Support for systemd tinc@.service instances
-------------------------------------------

On a legacy systems without ``systemd``, you can manage Tinc VPN networks using
the ``/etc/init.d/tinc`` init script.

If ``systemd`` is detected as the current init process, ``debops.tinc`` will
configure a set of ``systemd`` unit files:

``tinc.service``
  This is the main unit that manages all of the Tinc VPN networks and
  propagates start/stop/restart events.

``tinc@.service``
  This unit can be used to manage individual Tinc networks. The unit argument
  is the name of the VPN.

With ``systemd``, you can manage each Tinc network separately by issuing
commands::

    systemctl status tinc@mesh0
    systemctl start tinc@mesh0
    systemctl stop tinc@mesh0

