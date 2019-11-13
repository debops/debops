.. _owncloud__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.owncloud` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=nextcloud <owncloud__ldap_self_rdn>`

- :ref:`ou=Roles <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - ``cn=Password Reset Agent``

    - ``roleOccupant``: :envvar:`uid=nextcloud,cn=host.example.org,... <owncloud__ldap_binddn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=nextcloud <owncloud__ldap_self_rdn>`

  - :ref:`debops.owncloud`: :envvar:`Object Classes <owncloud__ldap_self_object_classes>`, :envvar:`Attributes <owncloud__ldap_self_attributes>`

Custom objectClasses and attributes from the :ref:`nextcloud
<slapd__ref_nextcloud>` LDAP schema:

- objectClass ``nextcloudAccount``, attributes ``nextcloudEnabled``, ``nextcloudQuota``
- objectClass ``nextcloudGroup``, attributes ``nextcloudEnabled``


.. _owncloud__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.owncloud` role, and specifies other roles with the same access
control rules:

- objectClass ``authorizedServiceObject``, attribute ``authorizedService``:

  - ``nextcloud``
  - ``owncloud``
  - ``web-public``
  - ``*`` (all services)

LDAP filter definition: :envvar:`owncloud__ldap_login_filter`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`owncloud__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`owncloud__ldap_device_dn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.owncloud` Ansible role.
