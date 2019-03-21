.. _slapd__ref_ldap_dit:

LDAP Directory Information Tree
===============================

This document describes how the :ref:`debops.slapd` Ansible role fits in the
LDAP directory structure organized by DebOps.


Directory structure
-------------------

- :envvar:`DNS (example.org) <slapd__domain>`

  - ``rootDSE``

    - :envvar:`cn=config <slapd__default_tasks>`

      - ``cn=module{0}``

        - ``{0}back_mdb``

        - ``{1}syncprov``

        - ``{2}ppolicy``

      - :ref:`cn=schema <slapd__ref_ldap_schemas>`

        - ``core.schema``

        - ``cosine.schema``

        - :ref:`rfc2307bis.schema <slapd__ref_rfc2307bis>`

        - ``inetorgperson.schema``

        - :ref:`posixgroupid.schema <slapd__ref_posixgroupid>`

        - :ref:`openssh-lpk.schema <slapd__ref_openssh_lpk>`

        - :ref:`ldapns.schema <slapd__ref_ldapns>`

      - ``olcDatabase={0}config``

        - ``olcOverlay={0}syncprov``

      - ``olcDatabase={1}mdb``

        - ``olcOverlay={0}syncprov``

        - ``olcOverlay={1}ppolicy``

        - :envvar:`olcAccess <slapd__acl_tasks>` (:ref:`documentation <slapd__ref_acl>`)

    - :envvar:`dc=example,dc=org <slapd__base_dn>`


Parent node
-----------

There's no parent node defined for the OpenLDAP server.

Child nodes
-----------

There's no child nodes defined for the OpenLDAP server.
