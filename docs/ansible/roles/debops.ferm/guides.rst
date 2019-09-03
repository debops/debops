Guides and examples
===================

.. include:: ../../../includes/global.rst

.. contents::
   :local:
   :depth: 2

.. _ferm__ref_guide_gateway:

Configuring an Internet Gateway
-------------------------------

An Internet gateway is a host which is managing the access of a private
(internal) network to the (external) Internet. When running Linux as a gateway
host the correct setup of the required iptables rules is crucial. While there
exist dedicated Linux distributions for this task such as OpenWRT or IPFire,
it's also possible to use a regular Debian GNU/Linux system and configure it
through DebOps. Here a short overview about the basic steps for a simple
gateway configuration is given.

The gateway host should have at least two network interfaces connected to the
respective networks. In this guide the interface named ``eth0`` will be used
as external untrusted interface and ``eth1`` will be used as internal trusted
interface.

To follow this guide you should be familiar with DebOps and the way to configure
related Ansible variables. If you're not, you may first want to read the
:ref:`Getting Started guide <getting-started>`.


.. _ferm__ref_guide_gateway_packet_forwarding:

Packet Forwarding
~~~~~~~~~~~~~~~~~

The configuration of packet forwarding is done on a per-interface basis. You
can use the :ref:`debops.ferm` and :ref:`debops.ifupdown` Ansible roles to
configure the respective firewall rules and kernel parameters, or use the
:ref:`debops.ifupdown` role to configure network interfaces, which will include
packet forwarding rules when necessary, for example for all bridge interfaces.

In case every connection traversing the network boundaries should be
explicitly defined, set an empty rule list here::

    ferm__rules_forward: []

On the other hand it might be useful to start with a less restrictive
forwarding rule list which allows all outgoing traffic::

    ferm__rules_forward:
      - chain: 'FORWARD'
        type: 'accept'
        outerface_present: '{{ ferm__external_interfaces }}'
        weight: '10'
        role: 'forward'
        role_weight: '20'
        name: 'external_out'
        comment: 'Forward outgoing traffic to other hosts'
        rule_state: '{{ "present" if (
                          (ferm__forward|d(ferm_forward) | bool) or
                          (ansible_local|d() and ansible_local.ferm|d() and
                           ansible_local.ferm.forward | bool))
                         else "absent" }}'

Once a packet was accepted by the firewall all related packets belonging to
the same connection are accepted too. This is defined in the
``connection_tracking`` rule which is loaded as part of the
:envvar:`ferm__default_rules` rule list.


.. _ferm__ref_guide_gateway_port_forwarding:

Port Forwarding
~~~~~~~~~~~~~~~

If the forward rules above are properly implemented, all external access to a
host connected to the internal network is blocked. Still it might be necessary
to allow external access to a specific internally hosted service such as a Web
server. This can be done by forwarding a port or port range from the gateway's
external interface to an internal host. Technically this is called DNAT
(Destination Network Address Translation), where the original destination
address of a network packet is rewritten to the internal host address.

* To forward the HTTP port from the gateway to the internal host, a rule such as
  the following is required:

.. code-block:: yaml

   ferm__host_rules:
     - type: 'dmz'
       name: 'http-forward'
       domain: [ 'ip' ]
       public_ip: '{{ ansible_eth0.ipv4.address }}'
       private_ip: '{{ lookup("dig", "web.internal.example.com") }}'
       protocol: 'tcp'
       ports: [ 80 ]

.. topic:: Note

    :ref:`ferm__ref_type_dmz` rule template won't modify the source address of a
    forwarded packet by default. This means that the original source address can
    still be identified at the internal receiver, however the route leading back to
    the source address must traverse the gateway again in order to successfully
    initiate connection tracking.

    The optional ``snat_ip`` parameter can be used to configure source address
    translation (SNAT).

.. _ferm__ref_guide_gateway_services:

INPUT Rules for Services running on the Gateway Host
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As an Internet gateway is usually a device which is running 24/7 and being a
core part of the network infrastructure, people might want to run additional
services on this host. In case these services are also managed by DebOps
the respective Ansible roles will ensure that the required firewall rules are
added to the :envvar:`ferm__dependent_rules` rule list. By default access from
all networks is allowed which is not always desired. Below it will be shown how
this can be restricted to the internal network attached to ``eth1``.

**Example: dnsmasq**

The debops.dnsmasq_ role is providing DNS and DHCP services. Obviously access
to these services should only be allowed from the internal network.

* Define the upstream (external) interface where access should be blocked::

    dnsmasq_upstream_interfaces: [ 'eth0' ]

* Define the internal interface where the DNS and DHCP services will be
  provided. This setting would automatically define the necessary :command:`iptables`
  ``INPUT`` rules for those services to be accessible from the internal
  network::

    dnsmasq_interfaces:
      - interface: 'eth1'
        name: 'gateway'
        dhcp_range_start: '10'
        dhcp_range_end: '-10'
        dhcp_lease: '24h'

Refer to the debops.dnsmasq_ role for details.

**Example: nginx**

Most other DebOps roles which manage applications are able to restrict access
through the firewall based on source IP addresses and network ranges. This is
typically done by defining a corresponding ``service_allow`` variable. In case
of debops.nginx_ this configuration would look as following::

    nginx_allow: [ '{{ ansible_eth1.ipv4.network }}/{{ ("0.0.0.0/" + ansible_eth1.ipv4.netmask) | ipaddr("prefix") }}' ]

This will restrict access to the HTTP service running on the gateway host to
the internal IPv4 network which is automatically defined using the ``ansible_eth1``
host fact.


.. _ferm__ref_guide_gateway_output:

Restrict Outgoing Traffic
~~~~~~~~~~~~~~~~~~~~~~~~~

Many :command:`iptables` setups are rather lax when it's about restricting outgoing
traffic. By default DebOps will set the iptables ``OUTPUT`` policy to ``ACCEPT``
which will permit every outgoing connection attempt. However, it is always a
good idea to also limit the connections which can be made from within a host,
especially if the host is directly connected to the Internet.

Unfortunately ``debops.ferm`` doesn't provide any predefined rule lists to
restrict outgoing traffic, therefore they need to be custom defined entirely.
On the other hand this will be a good example for defining rule lists also for
any other purpose.

* First create an Ansible list with an individually chosen name which will
  hold the custom output rules. For every outgoing connection which should be
  allowed to the internal or external network a rule needs to be added. Every
  template described in the :ref:`ferm__ref_rule_types` chapter can be used for the
  custom rules. The definition below is just a minimal example to show the
  procedure::

    ferm__custom_rules_filter_output:

      - type: 'accept'
        chain: 'OUTPUT'
        weight: '00'
        weight_class: 'loopback'
        comment: 'Allow connections to loopback'
        name: 'loopback_out'
        outerface: 'lo'
        target: 'ACCEPT'

      - type: 'accept'
        chain: 'OUTPUT'
        weight: '50'
        weight_class: 'any-service'
        comment: 'Allow connections to internal network'
        name: 'internal_out'
        outerface: 'eth1'
        target: 'ACCEPT'

      - type: 'accept'
        chain: 'OUTPUT'
        weight: '03'
        weight_class: 'filter-icmp'
        comment: 'Allow outgoing ICMP requests'
        name: 'icmp_out'
        protocol: 'icmp'
        outerface: 'eth0'
        target: 'ACCEPT'

      - type: 'accept'
        chain: 'OUTPUT'
        weight: '32'
        comment: 'Allow outgoing DNS traffic'
        name: 'dns_out'
        protocol: 'udp'
        dport: 53
        outerface: 'eth0'
        target: 'ACCEPT'

      - type: 'reject'
        chain: 'OUTPUT'
        weight_class: 'any-reject'
        name: 'reject_out'
        comment: 'Reject remaining outgoing traffic'

  The last rule is using :ref:`ferm__ref_type_reject` which will reject
  every packet not explicitly allowed. This will make it easier to figure out
  missing rules than if the packets would simply be dropped.

* Reference the custom rule list in one of the main rule list variables
  :envvar:`ferm__rules`, :envvar:`ferm__group_rules` or
  :envvar:`ferm__host_rules`. E.g.::

    ferm__host_rules: '{{ ferm__custom_rules_filter_output }}'

  If there are multiple custom rule lists, they can be concatenated with ``+``.

* Finally set the iptables ``OUTPUT`` policy to ``DROP``::

    ferm__default_policy_output: 'DROP'


.. _ferm__ref_guide_gateway_hardening:

Block Port Scans
~~~~~~~~~~~~~~~~

To block port scans there is a predefined rule ``block_portscans`` which is not
enabled by default.
It will remember source addresses which try to reach closed ports and
completely blocks access from those addresses for a while. This behaviour can
be enabled by setting :envvar:`ferm__mark_portscan`::

    ferm__mark_portscan: True

To make sure management access to the gateway is not suddenly blocked by the
mentioned rule list, trusted addresses must be whitelisted. For example when
trying out DebOps in a Vagrant environment the host running :command:`vagrant``
should be added to the :envvar:`ferm__ansible_controllers` variable. Otherwise
:command:`vagrant ssh` might suddenly be blocked by the portscan rule in case
a machine port was mistakenly accessed where no service was running::

    ferm__ansible_controllers: [ '192.168.121.1' ]

The host running DebOps doesn't explicitly need to be added here as it is
automatically being whitelisted.
