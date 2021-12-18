.. Copyright (C) 2021 Imre Jonk <imre@imrejonk.nl>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

The default configuration assumes that the target host has been configured with
:ref:`debops.postgresql_server`.

Without any additional configuration, the ``service/pdns`` playbook will
configure a PostgreSQL role on the target host, create a database and
initialize it with the pdns PostgreSQL schema, install PowerDNS Authoritative
Server, and set it up using the ``gpgsql`` backend. The only mode of operation
available will be native replication (i.e. pdns relies on the backend doing the
replication of zone data to other pdns servers).

Modes of operation
------------------

pdns has four modes of operation: native replication, primary operation,
secondary operation, and autosecondary operation. A brief description of each
mode follows. For full details, refer to the `DNS Modes of Operation
documentation`__.

.. __: https://doc.powerdns.com/authoritative/modes-of-operation.html

Native replication
~~~~~~~~~~~~~~~~~~

Native replication does not need to be enabled. It is always available,
provided that your backend supports it. With native replication, pdns just lets
the backend figure out how to get the zone data to the backends of your other
pdns servers.

Primary operation
~~~~~~~~~~~~~~~~~

Primary operation can be enabled by setting :envvar:`pdns__primary` to
``True``. Doing so will instruct pdns to send (optionally TSIG-signed)
notifications of changes to secondaries, which can then initiate zone
transfers. Notifications are only sent for domains with type MASTER in your
backend.

Secondary operation
~~~~~~~~~~~~~~~~~~~

Secondary operation can be enabled by setting :envvar:`pdns__secondary` to
``True``. Doing so will instruct pdns to periodically check for zone changes at the primary nameservers, and update the local zones accordingly. These checks happen every 'refresh' seconds (as specified by the SOA record) and are only performed for domains with type SLAVE in your backend. Additionally, if the primary
nameserver sends notifications for such domains, pdns will initiate a zone
transfer immediately.

Autosecondary operation
~~~~~~~~~~~~~~~~~~~~~~~

Autosecondary operation can be enabled by setting :envvar:`pdns__autosecondary`
to ``True``. Doing so will instruct pdns to automatically provision domains
that it receives notifications for, if the notifications come from an IP
address listed in the 'supermasters' table in your backend database. pdns will
then act as a secondary for those domains.

Dynamic DNS Update (RFC 2136)
-----------------------------

Dynamic DNS Update (:rfc:`2136`) allows for changing authoritative zone data in
a standardized way. It works by having a client send a DNS UPDATE message to
the primary nameserver, which, after optional IP allowlist and/or transaction
signature (TSIG) checking, updates the zone in whatever way the DNS UPDATE
message tells it to. One service that supports sending these messages is the
ISC DHCP Server, represented in the :ref:`debops.dhcpd` role.

The ``debops.pdns`` role enables support for the DNS UPDATE mechanism by
default, but also denies all DNS updates unless an IP allowlist or TSIG key has
been specified in the domain metadata. If you want to allow all DNS updates
from a list of IP ranges, see :envvar:`pdns__allow_dnsupdate_from`. For
per-domain metadata related to DNS updates, see
https://doc.powerdns.com/authoritative/dnsupdate.html#per-zone-settings

Note that not all pdns backends support DNS updates.

DNSSEC
------

When operating in primary or native replication mode, pdns can perform online
signing of zone data, i.e. signed responses are generated on-the-fly. These
responses are cached internally. In much the same fashion, pdns can operate as
a "bump-in-the-wire" front-signing server between a legacy (non-DNSSEC-capable)
authoritative server and its clients.

A secondary pdns server can perform a DNSSEC-capable zone transfer, i.e. it
stores and serves pre-signed zone data which it received from the primary.

There is also BIND-mode operation, which takes a traditional BIND-style zone
file and signs it using DNSSEC keys stored in another backend.

The default setup when signing a zone with ``# pdnsutil secure-zone`` is a
single ECDSAP256SHA256 key that is used as a Combined-Signing Key (CSK), with
NSEC as the negative answer strategy. NSEC3 is also supported. If you use pdns,
a split-key setup most likely makes little sense, but you can do it if you
really want to.

**Important caveats** regarding DNSSEC support in pdns:

- When operating in online signing mode, the default pdns configuration will
  not increase the SOA serial when signatures are being rolled. This is not a
  problem in the default native replication mode. For primary operation
  however, you need to pick a SOA-EDIT value to ensure signature freshness on
  secondaries. Please refer to the `SOA-EDIT documentation`__ for this.

- In online-signing mode, the ALIAS record type is not supported.

.. __: https://doc.powerdns.com/authoritative/dnssec/operational.html#soa-edit-ensure-signature-freshness-on-slaves

Anyone using pdns to serve DNSSEC-signed zone data is encouraged to read the
DNSSEC guide: https://doc.powerdns.com/authoritative/dnssec/index.html

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.pdns`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/pdns.yml
   :language: yaml
   :lines: 1,5-
