.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _netbox__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.netbox` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=netbox <netbox__ldap_self_rdn>`

    - :envvar:`ou=Groups <netbox__ldap_groups_rdn>` (:envvar:`conditional <netbox__ldap_private_groups>`)

      - :envvar:`cn=NetBox Users <netbox__ldap_user_group_rdn>`

        - ``member``: :envvar:`uid=user,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

      - :envvar:`cn=NetBox Active Users <netbox__ldap_user_active_group_rdn>`

        - ``member``: :envvar:`uid=user,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

      - :envvar:`cn=NetBox Staff <netbox__ldap_user_staff_group_rdn>`

        - ``member``: :envvar:`uid=staff,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

      - :envvar:`cn=NetBox Administrators <netbox__ldap_user_admin_group_rdn>`

        - ``member``: :envvar:`uid=admin,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

- :ref:`ou=Groups <ldap__ref_ldap_dit>` -> :ref:`debops.ldap` (:envvar:`conditional <netbox__ldap_private_groups>`)

  - :envvar:`cn=NetBox Users <netbox__ldap_user_group_rdn>`

    - ``member``: :envvar:`uid=user,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

  - :envvar:`cn=NetBox Active Users <netbox__ldap_user_active_group_rdn>`

    - ``member``: :envvar:`uid=user,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

  - :envvar:`cn=NetBox Staff <netbox__ldap_user_staff_group_rdn>`

    - ``member``: :envvar:`uid=staff,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`

  - :envvar:`cn=NetBox Administrators <netbox__ldap_user_admin_group_rdn>`

    - ``member``: :envvar:`uid=admin,ou=People,dc=example.dc.org <netbox__ldap_object_ownerdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=netbox <netbox__ldap_self_rdn>`

  - :ref:`debops.netbox`: :envvar:`Object Classes <netbox__ldap_self_object_classes>`, :envvar:`Attributes <netbox__ldap_self_attributes>`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`netbox__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`netbox__ldap_device_dn`

  - :envvar:`ansible_local.ldap.people_rdn <ldap__people_rdn>` -> :envvar:`netbox__ldap_people_rdn`

  - :envvar:`ansible_local.ldap.groups_rdn <ldap__groups_rdn>` -> :envvar:`netbox__ldap_groups_rdn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.netbox` Ansible role.
