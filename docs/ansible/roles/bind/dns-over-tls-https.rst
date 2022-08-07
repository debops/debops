.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _bind__ref_dot_doh:

DNS over TLS/HTTP(S)
====================

.. include:: ../../../includes/global.rst

.. only:: html

   .. contents::
      :local:


.. _bind__ref_dot_doh_introduction:

Introduction
------------

Another relatively novel feature in BIND is DNS over TLS (DoT, :rfc:`7858`) and
DNS over HTTP(S) (DoH, :rfc:`8484`). DNS over DTLS (read: UDP, :rfc:`8094`) and
DNS over HTTP3/QUIC (DoH3/DoQ, :rfc:`9250`) are currently not supported.

These standards provide some level of protection of traffic between a querier
and a server against eavesdropping and tampering (DNSSEC does not protect
against the former).

If the feature ``dot`` (DNS over TLS) is enabled in :envvar:`bind__features`,
BIND will be configured to listen to incoming DNS queries over a separate
TCP port (default: ``853``).

If the feature ``doh_https`` (DNS over HTTPS) is enabled, BIND will be
configured to listen to incoming DNS queries over HTTPS. This means that
BIND will listen to the standard HTTPS port (``443``) for queries on
the paths defined in :envvar:`bind__doh_endpoints`.

Both ``dot`` and ``doh_https`` setups rely on the certificates provided by
Public Key Infrastructure setup by the :ref:`debops.pki` role.

Since ``doh_https`` will render the HTTPS port unusable to other roles
(notably, web servers), a separate ``doh_proxy`` mode is also available.
In this mode, BIND will only listen to a port (see
:envvar:`bind__doh_proxy_port`) on the loopback interface. This can then be
used by a local webserver to forward DNS queries to the BIND server. Currently,
only :ref:`debops.nginx` is supported.

In addition, or separately, ``stats_proxy`` also makes detailed statistics
available over the same proxy (using :envvar:`bind__stats_proxy_port` on the
loopback interface).

.. note::
   Both ``doh_proxy`` and ``stats_proxy`` mean that incoming connections
   will be considered to originate from the loopback address. This means that
   care has to be taken to make sure that ACLs, IP matches, etc in the BIND
   configuration are correct so that e.g. external views are not inadvertently
   exposed over the DoH interface provided by the web proxy.

Finally, a ``doh_http`` (DNS over HTTP, i.e. unencrypted) mode is available.
Since this mode offers no encryption, it is mostly meant for debugging and
testing.


.. _bind__ref_dot_doh_testing:

Testing
-------

If you want to test DNS over TLS/HTTPS/HTTP, the :command:`kdig` utility
from the ``knot-dnsutils`` Debian package can be used (the examples below
assume that the DNS server is ``dns.example.com`` and that it has a
valid certificate, you can also use the ``+tls-ca=<path>`` argument
to pass a valid CA certificate to :command:`kdig`):

.. code-block:: console

   # kdig 1.0.0.127.in-addr.arpa. PTR @dns.example.com
   ;; ->>HEADER<<- opcode: QUERY; status: NOERROR; id: 18529
   ;; Flags: qr aa rd; QUERY: 1; ANSWER: 1; AUTHORITY: 0; ADDITIONAL: 0

   ;; QUESTION SECTION:
   ;; 1.0.0.127.in-addr.arpa.		IN	PTR

   ;; ANSWER SECTION:
   1.0.0.127.in-addr.arpa.	604800	IN	PTR	localhost.

   ;; Received 63 B
   ;; Time 2022-08-08 20:29:17 CEST
   ;; From 192.168.2.1@53(UDP) in 29.3 ms

   # kdig 1.0.0.127.in-addr.arpa. PTR @dns.example.com +tls
   ;; TLS session (TLS1.3)-(ECDHE-SECP256R1)-(RSA-PSS-RSAE-SHA256)-(AES-256-GCM)
   ;; ->>HEADER<<- opcode: QUERY; status: NOERROR; id: 50232
   ;; Flags: qr aa rd; QUERY: 1; ANSWER: 1; AUTHORITY: 0; ADDITIONAL: 1

   ;; EDNS PSEUDOSECTION:
   ;; Version: 0; flags: ; UDP size: 1232 B; ext-rcode: NOERROR
   ;; EDE: 18 (Prohibited)

   <snip question and answer section>

   ;; Received 80 B
   ;; Time 2022-08-08 20:29:21 CEST
   ;; From 192.168.2.1@853(TCP) in 103.5 ms

   $ kdig 1.0.0.127.in-addr.arpa. PTR @dns.example.com +https=dns.example.com/dns-query
   ;; TLS session (TLS1.3)-(ECDHE-SECP384R1)-(RSA-PSS-RSAE-SHA256)-(AES-256-GCM)
   ;; HTTP session (HTTP/2-POST)-(dns.example.com/dns-query)-(status: 200)
   ;; ->>HEADER<<- opcode: QUERY; status: NOERROR; id: 0
   ;; Flags: qr aa rd ra; QUERY: 1; ANSWER: 1; AUTHORITY: 0; ADDITIONAL: 1

   ;; EDNS PSEUDOSECTION:
   ;; Version: 0; flags: ; UDP size: 1232 B; ext-rcode: NOERROR

   <snip question and answer section>

   ;; Received 74 B
   ;; Time 2022-08-08 20:34:45 CEST
   ;; From 192.168.2.1@443(TCP) in 56.2 ms


.. _bind__ref_dot_doh_client_support:

Client support
--------------

Setting up BIND with support for DoT/DoH is, of course, just one piece of the
puzzle.  Clients also need to make use of these protocols. Notable examples of
Linux clients which provides such support include :command:`systemd-resolved`
(see :man:`systemd-resolved(8)` and the ``DNSOverTLS`` option in
:man:`resolved.conf(5)`) which can provide network name resolution to local
clients over DoT.

Work is also under way to draft standards which would allow clients to
automatically discover that a given DNS server/resolver supports protocols
such as DoT/DoH/DoQ. Notable examples include `DDR`__, which adds new records
to zones indicating the protocols supported by the name server, and `DNR`__,
which define new DHCP and IPv6 Router Advertisement (RA) options for
announcing the availability of encrypted DNS resolvers.

.. __: https://datatracker.ietf.org/doc/html/draft-ietf-add-ddr
.. __: https://datatracker.ietf.org/doc/html/draft-ietf-add-dnr


.. _bind__ref_dot_doh_drawbacks:

Drawbacks
---------

As can be seen from the above :command:`kdig` examples (plain DNS, DoT, DoH),
there may be some extra overhead (latency) incurred by DoT/DoH compared to
plain DNS (and there are other factors and tradeoffs to consider, such as "head
of queue blocking", long message support, privacy, etc). The latency is,
however, partially amortized by the fact that TCP connections can be kept open
over a longer time period and reused for several queries.

Most of these potential drawbacks are expected to be addressed, or at least
ameliorated, by new standards such as DNS over QUIC/HTTP3 (DoQ/DoH3,
:rfc:`9250`), for more details see these two articles: `first`__, `second`__.

.. __: https://blog.nlnetlabs.nl/newsletter-dns-over-quic/
.. __: https://blog.cloudflare.com/the-road-to-quic/

Unfortunately, DoQ/DoH3 is not yet supported by BIND (or common Linux clients),
but that is likely to change in the future.


.. _bind__ref_dot_doh_firefox:

Clients using external DoT/DoH servers
--------------------------------------

Another drawback with DoT/DoH is that there are clients which may make use of
external DNS servers via DoT/DoH, which breaks split-view/internal DNS (i.e.
situations where a local DNS server presents a different, usually more complete
view, to internal clients).

One notable example of a client which, by default, ignores the system-defined
resolvers, instead sending all DNS queries to predefined external DoH providers
is `Firefox`__, as explained in `this blog post`__. Mozilla also included
support for `turning off this feature`__ by using a so-called "canary domain".

.. __: https://www.mozilla.org/en-US/firefox/
.. __: https://blog.mozilla.org/futurereleases/2019/09/06/whats-next-in-making-dns-over-https-the-default/
.. __: https://support.mozilla.org/en-US/kb/configuring-networks-disable-dns-over-https

In short, if the local name server returns ``NXDOMAIN`` for the special-purpose
domain ``use-application-dns.net.``, Firefox will fall back to using the
system-defined resolvers.

The defaults provided by this role includes an example of blocking such
special-purpose domains using BINDs `Response Policy Zone (RPZ) Rewriting`__
feature (see :envvar:`bind__blocked_domains` and its use in
:envvar:`bind__default_zones` and :envvar:`bind__default_configuration`).

.. __: https://bind9.readthedocs.io/en/latest/reference.html#response-policy-zone-rpz-rewriting

This is, of course, not a perfect solution. First, it is Firefox-specific and
other applications may use different mechanisms (for example, Chrome uses the
system-defined DNS resolver but may `auto-upgrade to DoH`__). Second, some
clients (including malware) may offer no mechanism at all, meaning that DoT/DoH
using external servers will have to be blocked using other means (such as
firewall rules). That is, however, outside the scope of this role.

.. __: https://www.chromium.org/developers/dns-over-https/
