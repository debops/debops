.. Copyright (C) 2021 Imre Jonk <imre@imrejonk.nl>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The ``debops.pdns`` role can be used to configure `PowerDNS Authoritative
Server`_, whose service is called 'pdns' in Debian. pdns supports multiple
backends like major relational databases, LDAP servers and plain text files.
Backends that support native replication can be used in place of traditional
zone transfers. Furthermore, pdns can be used for geographical load balancing
and has excellent DNSSEC support, currently supporting the vast majority of
DNSSEC-enabled domains in Europe. pdns is extensible using a wide variety
of scripting languages.

.. _PowerDNS Authoritative Server: https://www.powerdns.com/auth.html
