Getting started
===============


Default configuration
---------------------

If the :ref:`debops.lxc` role has set up a LXC environment on the host, the
:ref:`debops.unbound` will configure an internal DNS zone based on the
configuration provided by the :ref:`debops.lxc` Ansible local facts. This can
be used to access the LXC containers via their DNS names instead of IP
addresses.


Usage with internal RFC 1918 private networks
---------------------------------------------

This role does not configure any upstream DNS servers by default (for example
Google DNS servers). This means that Unbound will try and resolve DNS and
DNSSEC queries by itself, using the locally provided DNS root keys for DNSSEC
verification. On the Debian/Ubuntu hosts, when the ``unbound`` service starts,
it replaces the currently configured DNS servers with itself, using the
:command:`resolvconf` package.

This means that any private networks the host is connected to won't be
resolvable anymore. If the default FQDN of the host is in a private network,
the host's hostname and domain won't be resolvable either - this affects
:command:`sudo` and Ansible operation, among other things.

To avoid that, as long as you have configured local DNS nameserver for an
internal domain with revDNS records, for example :command:`dnsmasq`, you can
add your private network as an insecure, transparent DNS zone:

.. code-block:: yaml

   unbound__zones:

     - name:       'internal-network'
       zone:       'nat.example.org.'
       revdns:     '192.0.2.0/24'
       nameserver: '192.0.2.1'

The above configuration will tell Unbound to forward all DNS queries for
``nat.example.org.`` and ``0.2.0.192.in-addr.arpa.`` DNS zones to the
``192.0.2.1`` nameserver.

If the specified ``revdns`` subnet is in the private IP address range (RFC
1918), the configuration template will make sure that the specified subnet and
domain zones are configured as ``transparent``, which will tell Unbound to
serve the responses from the upstream DNS server as usual.  These zones will
also be marked as insecure, to avoid issues with DNSSEC validation.

It's possible to use a bigger subnet size than ``/24`` - subnets between
``/16`` and ``/24`` will have multiple ``/24`` reverse DNS zones pointed to the
specified nameserver. Bigger subnets however currently don't work correctly due
to the ``netaddr`` Python library used to generate the correct DNS zone names
using only class C addresses (``/24`` CIDR subnets).


Example inventory
-----------------

The install and configure Unbound on a host, it needs to be present in the
``[debops_service_unbound]`` Ansible inventory group:

.. code-block:: none

   [debops_service_unbound]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.unbound`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/unbound.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::unbound``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
