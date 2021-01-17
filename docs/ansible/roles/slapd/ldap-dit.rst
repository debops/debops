.. Copyright (C) 2016-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

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

        - ``{3}unique``

        - ``{4}memberof``

        - ``{5}refint``

        - ``{6}auditlog``

        - ``{7}constraint``

        - ``{8}back_monitor``

        - ``{9}lastbind``

        - ``{10}autogroup``

      - :ref:`cn=schema <slapd__ref_ldap_schemas>`

        - :ref:`core.schema <slapd__ref_initial_schemas>`

        - :ref:`cosine.schema <slapd__ref_initial_schemas>`

        - :ref:`rfc2307bis.schema <slapd__ref_rfc2307bis>`

        - :ref:`inetorgperson.schema <slapd__ref_initial_schemas>`

        - :ref:`debops.schema <slapd__ref_debops_schema>`

        - :ref:`posixgroupid.schema <slapd__ref_posixgroupid>`

        - :ref:`nextuidgid.schema <slapd__ref_nextuidgid_schema>`

        - :ref:`orgstructure.schema <slapd__ref_orgstructure_schema>`

        - :ref:`ppolicy.schema <slapd__ref_ppolicy_schema>`

        - :ref:`ldapns.schema <slapd__ref_ldapns>`

        - :ref:`groupofentries.schema <slapd__ref_groupofentries>`

        - :ref:`openssh-lpk.schema <slapd__ref_openssh_lpk>`

        - :ref:`sudo.schema <slapd__ref_sudo>`

        - :ref:`eduperson.schema <slapd__ref_eduperson>`

        - :ref:`nextcloud.schema <slapd__ref_nextcloud>`

        - :ref:`mailservice.schema <slapd__ref_mailservice>`

        - :ref:`dyngroup.schema <slapd__ref_dyngroup>`

        - :ref:`freeradius.schema <slapd__ref_freeradius_schema>`
          (with RADIUS Client/Profile/Accounting, DHCPv4, DHCPv6 schema)

      - ``olcDatabase={0}config``

        - :ref:`olcOverlay={0}syncprov <slapd__ref_syncprov_overlay>` (:ref:`for Multi-Master replication <slapd__ref_syncrepl_multi_master>`)

      - ``olcDatabase={1}mdb``

        - :ref:`olcOverlay={0}syncprov <slapd__ref_syncprov_overlay>` (:ref:`for Multi-Master replication <slapd__ref_syncrepl_multi_master>`)

        - :ref:`olcOverlay={1}ppolicy <slapd__ref_ppolicy_overlay>`

        - :ref:`olcOverlay={2}unique <slapd__ref_unique_overlay>`

        - :ref:`olcOverlay={3}memberof <slapd__ref_memberof_overlay>` (for ``groupOfNames`` LDAP objects)

        - :ref:`olcOverlay={4}memberof <slapd__ref_memberof_overlay>` (for ``groupOfEntries`` LDAP objects)

        - :ref:`olcOverlay={5}memberof <slapd__ref_memberof_overlay>` (for ``groupOfURLs`` LDAP objects)

        - :ref:`olcOverlay={6}memberof <slapd__ref_memberof_overlay>` (for ``organizationalRole`` LDAP objects)

        - :ref:`olcOverlay={7}refint <slapd__ref_refint_overlay>`

        - :ref:`olcOverlay={8}auditlog <slapd__ref_auditlog_overlay>`

        - :ref:`olcOverlay={9}constraint <slapd__ref_constraint_overlay>`

        - :ref:`olcOverlay={10}autogroup <slapd__ref_autogroup_overlay>`

        - :ref:`olcOverlay={11}lastbind <slapd__ref_lastbind_overlay>`

        - :envvar:`olcAccess <slapd__acl_tasks>` (:ref:`documentation <slapd__ref_acl>`)

      - ``olcDatabase={2}monitor``

    - :envvar:`dc=example,dc=org <slapd__base_dn>`


Parent nodes
------------

There are no parent nodes defined for the OpenLDAP server.

Child nodes
-----------

There are no child nodes defined for the OpenLDAP server.
