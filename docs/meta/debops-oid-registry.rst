.. _debops_oid_registry:

DebOps OID Registry
===================

This is the authoritative source of the information regarding the DebOps OID
Registry that describes the hierarchy of the Object Identifiers managed in
DebOps.

.. contents::
   :local:


Overview
--------

In order to extend specific network protocols like SNMP or LDAP, an
organization needs to have its own `Private Enterprise Number`__ registered at
`Internet Assigned Numbers Authority`__ (IANA) to avoid collisions with other
organizations present in the Internet.

.. __: https://en.wikipedia.org/wiki/Private_Enterprise_Number
.. __: https://en.wikipedia.org/wiki/Internet_Assigned_Numbers_Authority

enterprise.DebOps / 1.3.6.1.4.1.53622
-------------------------------------

DebOps is registered in the `Private Enterprise Numbers`__ registry as:

.. __: https://www.iana.org/assignments/enterprise-numbers/enterprise-numbers

.. code-block:: none

   1.3.6.1.4.1.53622 or iso.org.dod.internet.private.enterprise.DebOps

The technical contact for DebOps organization is Maciej Delmanowski.

The DebOps namespace is split into child namespaces depending on their purpose:

===== =========== ====================================================
 OID   Namespace   Description
----- ----------- ----------------------------------------------------
42    DebOpsLDAP  Object definitions for LDAP databases (LDAP schemas)
===== =========== ====================================================

The DebOps namespace is defined in the :ref:`debops.schema
<slapd__ref_debops_schema>`. All other LDAP schemas created in the DebOps
project depend on this schema to be present in the LDAP directory.

enterprise.DebOps.DebOpsLDAP / 1.3.6.1.4.1.53622.42
---------------------------------------------------

The Object identifiers for LDAP objects managed by DebOps are defined in the
``42`` namespace.

===== ==================================================== ====================
 OID   LDAP schema                                          Ansible role
----- ---------------------------------------------------- --------------------
1     :ref:`posixgroupid.schema <slapd__ref_posixgroupid>`  :ref:`debops.slapd`
----- ---------------------------------------------------- --------------------
2     :ref:`mailservice.schema <slapd__ref_mailservice>`    :ref:`debops.slapd`
===== ==================================================== ====================

References
----------

- `Object identifier`__ Wikipedia page

  .. __: https://en.wikipedia.org/wiki/Object_identifier

- `Object identifier`__ description in LDAP Wiki

  .. __: https://ldapwiki.com/wiki/OID

- `OpenLDAP OID hierarchy`__

  .. __: https://www.openldap.org/faq/data/cache/197.html

- `Debian OID hierarchy`__

  .. __: https://dsa.debian.org/iana/
