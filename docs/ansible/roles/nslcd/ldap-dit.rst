.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _nslcd__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.nslcd` Ansible role fits in the
:ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=nslcd <nslcd__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=nslcd <nslcd__ldap_self_rdn>`

  - :ref:`debops.nslcd`: :envvar:`Object Classes <nslcd__ldap_self_object_classes>`, :envvar:`Attributes <nslcd__ldap_self_attributes>`


.. _nslcd__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.nslcd` role, and specifies other roles with the same access
control rules:

- objectClass ``hostObject``, attribute ``host``:

  - ``posix:all`` (all hosts)
  - ``posix:hostname.example.org``
  - ``posix:*.example.org``
  - ``posix:urn:<pattern>`` (see :envvar:`nslcd__ldap_posix_urns` variable)

LDAP filter definition: :envvar:`nslcd__ldap_host_filter`

These rules apply to UNIX accounts (``passwd`` database) as well as UNIX groups
(``group`` database). UNIX accounts or group without the specified ``host``
attribute values will not be present on a given host.


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`nslcd__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`nslcd__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.nslcd` Ansible role.
