.. _slapd__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.slapd` Ansible role fits in the
:ref:`ldap__ref_dit`.


Directory structure
-------------------

- :envvar:`DNS (example.org) <slapd__domain>`

  - :ref:`rootDSE <ldap__ref_ldap_dit>` -> :ref:`debops.ldap`

    - :envvar:`cn=config <slapd__default_tasks>`

      - ``cn=module{0}``

        - ``{0}back_mdb``

        - ``{1}syncprov`` (:ref:`for Multi-Master replication <slapd__ref_syncrepl_multi_master>`)

        - ``{2}ppolicy``

      - :ref:`cn=schema <slapd__ref_ldap_schemas>`

        - :ref:`core.schema <slapd__ref_initial_schemas>`

        - :ref:`cosine.schema <slapd__ref_initial_schemas>`

        - :ref:`rfc2307bis.schema <slapd__ref_rfc2307bis>`

        - :ref:`inetorgperson.schema <slapd__ref_initial_schemas>`

        - :ref:`posixgroupid.schema <slapd__ref_posixgroupid>`

        - :ref:`openssh-lpk.schema <slapd__ref_openssh_lpk>`

        - :ref:`ldapns.schema <slapd__ref_ldapns>`

      - ``olcDatabase={0}config``

        - ``olcOverlay={0}syncprov`` (:ref:`for Multi-Master replication <slapd__ref_syncrepl_multi_master>`)

      - ``olcDatabase={1}mdb``

        - ``olcOverlay={0}syncprov`` (:ref:`for Multi-Master replication <slapd__ref_syncrepl_multi_master>`)

        - ``olcOverlay={1}ppolicy``

        - :envvar:`olcAccess <slapd__acl_tasks>` (:ref:`documentation <slapd__ref_acl>`)

    - :envvar:`dc=example,dc=org <slapd__base_dn>`


Parent node
-----------

There's no parent node defined for the OpenLDAP server.

Child nodes
-----------

There's no child nodes defined for the OpenLDAP server.
