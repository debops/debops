.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2019-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`sssd` daemon, maintained by the `SSSD Project`__, is a spinoff
from the `FreeIPA Project`__ and provides a modern take on venerable daemons
such as :ref:`debops.nslcd`, :ref:`debops.nscd` and :man:`unscd(1)`. It is
used to look up user, group or other information stored in a number of
different databases, such as LDAP, Kerberos, FreeIPA, Active Directory, etc.
It is needed if you want to use the ``posixAccount`` and ``posixGroup`` LDAP
objects to authenticate to UNIX-like hosts.

.. __: https://sssd.io/
.. __: https://www.freeipa.org/

The ``debops.sssd`` Ansible role can be used to configure the :command:`sssd`
service on a host and, via :ref:`debops.ldap` role, create a bind account in
the LDAP directory used by :command:`sssd` to perform LDAP lookups.
