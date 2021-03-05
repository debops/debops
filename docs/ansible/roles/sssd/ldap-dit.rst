.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2019-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _sssd__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.sssd` Ansible role fits in the
:ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=sssd <sssd__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=sssd <sssd__ldap_self_rdn>`

  - :ref:`debops.sssd`: :envvar:`Object Classes <sssd__ldap_self_object_classes>`, :envvar:`Attributes <sssd__ldap_self_attributes>`


.. _sssd__ref_ldap_dit_access:

Access Control
--------------

The DebOps LDAP environment includes the
:ref:`'ldapns' schema <slapd__ref_ldapns>` which can be used to define access
control rules to services. The lists below define the attribute values which
will grant access to the service managed by the :ref:`debops.sssd` role, and
specifies other roles with the same access control rules:

- objectClass ``hostObject``, attribute ``host``:

  - ``posix:all`` (all hosts)
  - ``posix:hostname.example.org``
  - ``posix:*.example.org``
  - ``posix:urn:<pattern>`` (see :envvar:`sssd__ldap_posix_urns` variable)

LDAP filter definition: :envvar:`sssd__ldap_host_filter`

These rules apply to UNIX accounts (``passwd`` database) as well as UNIX groups
(``group`` database). UNIX accounts or group without the specified ``host``
attribute values will not be present on a given host.


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`sssd__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`sssd__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.sssd` Ansible role.
