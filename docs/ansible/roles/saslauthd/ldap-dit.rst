.. _saslauthd__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.saslauthd` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=saslauthd <saslauthd__ldap_self_rdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=saslauthd <saslauthd__ldap_self_rdn>`

  - :ref:`debops.saslauthd`: :envvar:`Object Classes <saslauthd__ldap_self_object_classes>`, :envvar:`Attributes <saslauthd__ldap_self_attributes>`


.. _saslauthd__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.saslauthd` role, and specifies other roles with the same
access control rules:

The ``smtpd`` LDAP profile
~~~~~~~~~~~~~~~~~~~~~~~~~~

- objectClass ``authorizedServiceObject``, attribute ``authorizedService``:

  - ``all`` (all services)
  - ``mail:send``

LDAP filter definition: :envvar:`saslauthd__ldap_default_profiles`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`saslauthd__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`saslauthd__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.saslauthd` Ansible role.
