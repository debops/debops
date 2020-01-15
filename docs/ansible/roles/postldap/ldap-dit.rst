.. _postldap__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.postldap` Ansible role fits in the
:ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=postfix <postldap__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=postfix <postldap__ldap_self_rdn>`

  - :ref:`debops.postldap`: :envvar:`Object Classes <postldap__ldap_self_object_classes>`, :envvar:`Attributes <postldap__ldap_self_attributes>`


.. _postldap__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.postldap` role, and specifies other roles with the same
access control rules:

- objectClass ``authorizedServiceObject``, attribute ``authorizedService``:

  - ``all`` (all services)
  - ``mail:receive``
  - ``mail:send``


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`postldap__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`postldap__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.postldap` Ansible role.
