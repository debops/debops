.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _resolved__ref_dnssd:

DNS-SD support in :command:`systemd-resolved`
=============================================

.. only:: html

   .. contents::
      :local:


Overview
--------

The :command:`systemd-resolved` service supports `DNS Service Discovery`__
using `Multicast DNS`__ protocol, similar to the one used by `Avahi`__ on Linux
and `Bonjour`__ on Apple macOS environments. Services can be advertised on
a `.local`__ DNS domain and discovered by compatible clients. The
:command:`resolvectl query` and :command:`resolvectl service` commands can be
used to find local services advertised by DNS-SD.

.. __: https://en.wikipedia.org/wiki/Zero-configuration_networking#DNS-SD
.. __: https://en.wikipedia.org/wiki/Multicast_DNS
.. __: https://en.wikipedia.org/wiki/Avahi_(software)
.. __: https://en.wikipedia.org/wiki/Bonjour_(software)
.. __: https://en.wikipedia.org/wiki/.local


Network configuration for Multicast DNS
---------------------------------------

For the ``mDNS`` support to work, it needs to be enabled globally in
:command:`systemd-resolved` (it is enabled by default). Then, support needs to
be enabled on specific network interfaces using :command:`systemd-networkd` to
tell :command:`systemd-resolved` on which interfaces it should advertise and
listen for DNS-SD traffic.

Here's an example network configuration for a host with Ethernet interface
which makes sure that Multicast DNS support is enabled. Configuration is applied
on the host using the :ref:`debops.networkd` Ansible role:

.. code-block:: yaml

   ---
   # File: ansible/inventory/host_vars/laptop/networkd.yml

   networkd__configuration

     - name: 'eth0.network'
       raw: |
         [Match]
         Name=eth0

         [Network]
         DHCP=yes
         MulticastDNS=yes

         [DHCPv4]
         UseDomains=yes
       state: 'present'

After configuring the network interface(s), users can check the state of
Multicast DNS using the :command:`resolvectl` command. An example output:

.. code-block:: console

   user@laptop:~$ resolvectl
   Global
          Protocols: +LLMNR +mDNS -DNSOverTLS DNSSEC=no/unsupported
   resolv.conf mode: stub

   Link 2 (eth0)
   Current Scopes: DNS LLMNR/IPv4 LLMNR/IPv6 mDNS/IPv4 mDNS/IPv6
        Protocols: +DefaultRoute +LLMNR +mDNS -DNSOverTLS DNSSEC=no/unsupported
      DNS Servers: 192.0.2.1
       DNS Domain: example.org

The ``+mDNS`` flag in the "Global" section indicates that Multicast DNS is
enabled in :command:`systemd-resolved` service. The same flag in the "Link"
section indicates that Multicast DNS traffic is accepted on a particular link.

Users also need to make sure that the ``mDNS`` multicast UDP traffic is
accepted by the firewall. The port to open is ``5353/udp`` (defined as ``mdns``
in :file:`/etc/services` database) and the destination addresses are
``224.0.0.251`` for IPv4 network and ``ff02::fb`` for IPv6 network. This
configuration should be automatically enabled by the :ref:`debops.ferm` role
included in DebOps.


Exploring the ``.local`` network
--------------------------------

When Multicast DNS support is enabled, it should be possible to ping other
hosts on the ``.local`` domain:

.. code-block:: console

   user@laptop:~$ ping -c 1 server.local
   PING server.local (192.0.2.12) 56(84) bytes of data.
   64 bytes from server.example.org (192.0.2.12): icmp_seq=1 ttl=64 time=0.841 ms

   --- server.local ping statistics ---
   1 packets transmitted, 1 received, 0% packet loss, time 0ms
   rtt min/avg/max/mdev = 0.841/0.841/0.841/0.000 ms

The :command:`resolvectl query` command can be used to find out what services
are advertised on the local network. Currently they will only show services
advertised on the same host the command is executed on:

.. code-block:: console

   user@laptop:~$ resolvectl query -p mdns --type=PTR _services._dns-sd._udp.local
   _services._dns-sd._udp.local IN PTR _workstation._tcp.local -- link: eth0
   _services._dns-sd._udp.local IN PTR _ssh._tcp.local         -- link: eth0
   _services._dns-sd._udp.local IN PTR _sftp-ssh._tcp.local    -- link: eth0

   -- Information acquired via protocol mDNS/IPv6 in 2.9ms.
   -- Data is authenticated: yes

A specific service type can be queried as well:

.. code-block:: console

   user@laptop:~$ resolvectl query -p mdns --type=PTR _ssh._tcp.local
   _ssh._tcp.local IN PTR laptop._ssh._tcp.local               -- link: eth0

   -- Information acquired via protocol mDNS/IPv6 in 457us.
   -- Data is authenticated: yes

Unfortunately, current UI for service discovery in :command:`systemd-resolved`
is limited, `there's no user-facing way to list discovered services`__ known to
the resolver. Users can debug this currently using :command:`journald` logs. In
one terminal, start viewing the logs of the :command:`systemd-resolved`
service:

.. code-block:: console

   user@laptop:~$ sudo journalctl -f -u systemd-resolved.service

In another terminal, send the ``USR1`` signal to the service to dump its cache
information in the logs:

.. code-block:: console

   user@laptop:~$ sudo killall -USR1 systemd-resolved

This should display information about other hosts seen in the ``.local``
network. The :command:`systemd` project developers are `working on an user
interface`__ for this functionality, it might be available in the future.

.. __: https://github.com/systemd/systemd/issues/14796
.. __: https://github.com/systemd/systemd/pull/18355

If the hostname of a given service is known, the :command:`resolvectl service`
command can be used to find out its SRV resource records published in DNS:

.. code-block:: console

   user@laptop:~$ resolvectl service server._ssh._tcp.local
   server._ssh._tcp.local: server.local:22 [priority=0, weight=0]
                           192.0.2.12                        -- link: eth0
                           (server/_ssh._tcp/local)

   -- Information acquired via protocol mDNS/IPv4 in 238.6ms.
   -- Data is authenticated: no

Users should be able to use the services as normal:

.. code-block:: console

   user@laptop:~$ ssh server.local
   The authenticity of host 'server.local (192.0.2.12)' can't be established.
   ECDSA key fingerprint is SHA256:fy8ZGpDIc2a4Zmd2eIcbGDyJttN4eY0pRMZeUl1S7No.
   Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
   Warning: Permanently added 'server.local,192.0.2.12' (ECDSA) to the list of known hosts.
   You have no mail.
   Last login: Fri Mar  3 12:24:57 2023 from laptop.example.org
   user@server:~$


Publishing services using DNS-SD
--------------------------------

To publish a service using DNS Service Discovery protocol, users can put
configuration files in the :file:`/etc/systemd/dnssd/` directory. The format of
the configuration files is described in the :man:`systemd.dnssd(5)` manual
page. The services will be published after the :command:`systemd-resolved`
service is restarted (there's no support for reloading).

An example configuration file which publishes the SSH service on port ``22/tcp``:

.. code-block:: ini

   # File: /etc/systemd/dnssd/ssh.dnssd

   [Service]
   Name=%H
   Type=_ssh._tcp
   Port=22

The "Name=" parameter will be used as the DNS Resource Record, this
is not a descriptive name. The ``%H`` variable will be expanded as the
hostname.

The :ref:`debops.resolved` role can be used to generate and publish these
files, see the :ref:`resolved__ref_units` documentation for more details. The
role publishes a few services by default, you can find their configuration in
the :envvar:`resolved__default_units` variable.

Alternatively, Ansible roles can handle the files themselves; just ensure that
the :file:`/etc/systemd/dnssd/` directory is present on the host and after the
file is created, restart the :command:`systemd-resolved` service. DebOps
provides a convenient handler for this in the :ref:`debops.global_handlers`
role.


Compatibility with Avahi
------------------------

The :command:`avahi-daemon` service and the DNS-SD publisher functionality of
the :command:`systemd-resolved` service are mutually exclusive and cannot work
reliably at the same time. To fix this issue, the :ref:`debops.avahi` role
configures the :command:`systemd-resolved` service to turn off ``mDNS`` support
via :command:`systemd` unit file override. This unfortunately breaks the
:command:`resolvectl query` and :command:`resolvectl service` support for the
``.local`` domain. Hostname resolution should still work via Avahi, and local
services can be published the usual way - refer to the :ref:`debops.avahi` role
documentation for details.
