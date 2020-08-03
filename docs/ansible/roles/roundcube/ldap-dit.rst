.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _roundcube__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.roundcube` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=roundcube <roundcube__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=roundcube <roundcube__ldap_self_rdn>`

  - :ref:`debops.roundcube`: :envvar:`Object Classes <roundcube__ldap_self_object_classes>`, :envvar:`Attributes <roundcube__ldap_self_attributes>`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`roundcube__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`roundcube__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.roundcube` Ansible role.
