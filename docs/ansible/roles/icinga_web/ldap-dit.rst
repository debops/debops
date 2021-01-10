.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _icinga_web__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.icinga_web` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=icingaweb <icinga_web__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=icingaweb <icinga_web__ldap_self_rdn>`

  - :ref:`debops.icinga_web`: :envvar:`Object Classes <icinga_web__ldap_self_object_classes>`, :envvar:`Attributes <icinga_web__ldap_self_attributes>`


.. _icinga_web__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.icinga_web` role, and specifies other roles with the same access
control rules:

- objectClass ``authorizedServiceObject``, attribute ``authorizedService``:

  - ``all`` (all services)
  - ``icingaweb``

LDAP filter definition: :envvar:`icinga_web__ldap_user_filter`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`gitlab__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`gitlab__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.icinga_web` Ansible role.
