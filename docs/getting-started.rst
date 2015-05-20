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

Hosts added in ``[debops_tinc]`` inventory group will have the ``tinc`` daemon
installed and configured. By default, role will exchange the public RSA keys
between all of the hosts in that group and define connections between all of
them, you can change that using ``tinc_inventory_hosts`` list variable.

::

    [debops_tinc]
    hostname1
    hostname2


Example playbook
----------------

Here's an example playbook which uses ``debops.tinc`` role::

    ---

    - name: Configure tinc VPN
      hosts: debops_tinc

      roles:
        - role: debops.tinc
          tags: tinc

Static vs DHCP connection type
------------------------------

By default, ``debops.tinc`` role configures a node to start its VPN interface
in a "DHCP" mode, without connecting to any other bridge interface, and ask the
mesh network for an IP address. If no DHCP server was configured, host might
hang indefinitely waiting for a DHCP response.

To avoid above issue, you need to configure at least one VPN host to work in
a "static" mode::

    tinc_connection_type: 'static'

In this mode, host will be configured to start the VPN interface with a dummy
``0.0.0.0`` IP address and connect it to a bridge, by default ``br2``. This
bridge can be created by ``debops.subnetwork`` role, which defaults to ``br2``
as well.

In the "static" mode, VPN interface will act as another Layer 2 connection on
the bridge and DHCP requests from the VPN will be passed along to a suitable
server. You can configure a DHCP/DNS server using ``debops.dnsmasq`` role.

RSA public key exchange
-----------------------

``debops.tinc`` role will automatically exchange public RSA VPN keys between
all hosts in group specified in ``tinc_inventory_hosts`` list variable,
provided that the host information as been gathered by Ansible. In other words,
to exchange the keys, you need to execute the Ansible run on all or part of the
hosts in the specified group::

    debops -l debops_tinc -t tinc

