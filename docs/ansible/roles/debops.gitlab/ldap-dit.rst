.. _gitlab__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.gitlab` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=gitlab <gitlab__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=gitlab <gitlab__ldap_self_rdn>`

  - :ref:`debops.gitlab`: :envvar:`Object Classes <gitlab__ldap_self_object_classes>`, :envvar:`Attributes <gitlab__ldap_self_attributes>`


.. _gitlab__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.gitlab` role, and specifies other roles with the same access
control rules:

- objectClass ``authorizedServiceObject``, attribute ``authorizedService``:

  - ``gitlab``
  - ``web-public``
  - ``*`` (all services)

LDAP filter definition: :envvar:`gitlab__ldap_user_filter`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`gitlab__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`gitlab__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.gitlab` Ansible role.
