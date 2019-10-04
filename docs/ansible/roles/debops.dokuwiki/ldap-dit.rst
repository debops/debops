.. _dokuwiki__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.dokuwiki` Ansible role fits in
the :ref:`ldap__ref_dit`.


Directory structure
-------------------

- :ref:`cn=host.example.org <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

  - :envvar:`uid=dokuwiki <dokuwiki__ldap_self_rdn>`

    - :envvar:`ou=Groups <dokuwiki__ldap_groups_rdn>` (:envvar:`conditional <dokuwiki__ldap_private_groups>`)

      - :envvar:`cn=DokuWiki Administrators <dokuwiki__ldap_admin_group_rdn>`

        - ``member``: :envvar:`uid=admin,ou=People,dc=example.dc.org <dokuwiki__ldap_object_ownerdn>`

- :ref:`ou=Groups <ldap__ref_ldap_dit>` -> :ref:`debops.ldap` (:envvar:`conditional <dokuwiki__ldap_private_groups>`)

  - :envvar:`cn=DokuWiki Administrators <dokuwiki__ldap_admin_group_rdn>`

    - ``member``: :envvar:`uid=admin,ou=People,dc=example.dc.org <dokuwiki__ldap_object_ownerdn>`


Object Classes and Attributes
-----------------------------

- :envvar:`uid=dokuwiki <dokuwiki__ldap_self_rdn>`

  - :ref:`debops.dokuwiki`: :envvar:`Object Classes <dokuwiki__ldap_self_object_classes>`, :envvar:`Attributes <dokuwiki__ldap_self_attributes>`


.. _dokuwiki__ref_ldap_dit_access:

Access Control
--------------

DebOps LDAP environment includes the :ref:`'ldapns' schema <slapd__ref_ldapns>`
which can be used to define access control rules to services. The lists below
define the attribute values which will grant access to the service managed by
the :ref:`debops.dokuwiki` role, and specifies other roles with the same access
control rules:

- objectClass ``authorizedServiceObject``, attribute ``authorizedService``:

  - ``dokuwiki``
  - ``web-public``
  - ``*`` (all services)

LDAP filter definition: :envvar:`dokuwiki__ldap_user_filter`


Parent nodes
------------

- :ref:`debops.ldap <ldap__ref_ldap_dit>`

  - :envvar:`ansible_local.ldap.base_dn <ldap__base_dn>` -> :envvar:`dokuwiki__ldap_base_dn`

  - :envvar:`ansible_local.ldap.device_dn <ldap__device_dn>` -> :envvar:`dokuwiki__ldap_device_dn`

  - :envvar:`ansible_local.ldap.people_rdn <ldap__people_rdn>` -> :envvar:`dokuwiki__ldap_people_rdn`

  - :envvar:`ansible_local.ldap.groups_rdn <ldap__groups_rdn>` -> :envvar:`dokuwiki__ldap_groups_rdn`


Child nodes
-----------

There are no child nodes defined for the :ref:`debops.dokuwiki` Ansible role.
