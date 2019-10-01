.. _slapd__ref_overlays:

OpenLDAP Overlays
=================

OpenLDAP server supports `overlays`__ which can be added to a LDAP database to
modify its functionality. The overlays listed below are enabled by the
:ref:`debops.slapd` role by default.

.. __: https://www.openldap.org/doc/admin24/overlays.html

.. contents::
   :local:


.. _slapd__ref_syncprov_overlay:

Sync Provider overlay
---------------------

The role will by default enable the `Sync Provider`__ (``syncprov``) dynamic
module and overlay, in both the ``cn=config`` configuration database, and the
main OpenLDAP database.

The Sync Provider functionality is used in different `data replication`__
strategies. Enabling it by default, even on a standalone OpenLDAP server,
should be harmless - the replication requires additional configuration defined
in each OpenLDAP database. The overlay is enabled first to keep the
``X-ORDERED`` index number consistent between the ``cn=config`` database and
the main database.

.. __: http://www.zytrax.com/books/ldap/ch6/syncprov.html
.. __: https://www.openldap.org/doc/admin24/replication.html

Manual page: :man:`slapo-syncprov(5)`


.. _slapd__ref_ppolicy_overlay:

Password Policy overlay
-----------------------

The :ref:`debops.slapd` role will by default import the ``ppolicy`` LDAP
schema, load the ``ppolicy`` dynamic module and enable the Password Policy
overlay in the main OpenLDAP database.

The `Password Policy`__ overlay is used to maintain the security and quality of
various passwords stored in the LDAP database. By default the overlay will
ensure that the cleartext passwords passed to the OpenLDAP server are hashed
using the algorithms specified in the ``olcPasswordHash`` parameter (salted
SHA-512 via :man:`crypt(3)` function is set by default by the
:ref:`debops.slapd` role).

The LDAP administrators can define default and custom Password Policies in the
main database, which can enforce additional password requirements, like minimum
password length, different types of characters used, lockout policy, etc.

.. __: https://www.zytrax.com/books/ldap/ch6/ppolicy.html

Manual page: :man:`slapo-ppolicy(5)`


.. _slapd__ref_unique_overlay:

Attribute Uniqueness overlay
----------------------------

The `Attribute Uniqueness overlay`__ is used to enforce that specific LDAP
attributes are unique acrosse the LDAP directory. The default configuration
enforces the uniqueness of the ``uidNumber`` and ``gidNumber`` attributes in
the entire LDAP directory, and the ``uid``, ``gid`` and ``mail`` attributes in
the ``ou=People,dc=example,dc=org`` subtree of the directory.

.. __: https://www.openldap.org/doc/admin24/overlays.html#Attribute%20Uniqueness

Manual page: :man:`slapo-unique(5)`


.. _slapd__ref_memberof_overlay:

Reverse Group Membership Maintenance overlay
--------------------------------------------

The `memberOf overlay`__ is used to update the LDAP objects of group members
when they are added or removed from a particular ``groupOfNames`` object.
Applications and services can search for objects with the ``memberOf``
attribute with specific values to get the list of groups a given user belongs
to.

.. __: https://www.openldap.org/doc/admin24/overlays.html#Reverse%20Group%20Membership%20Maintenance

Manual page: :man:`slapo-memberof(5)`


.. _slapd__ref_refint_overlay:

Referential Integrity overlay
-----------------------------

The `refint overlay`__ is used to update Distinguished Name references in other
LDAP objects when a particular object is renamed or removed. This ensures that
the references between objects in the LDAP database are consistent.

.. __: https://www.openldap.org/doc/admin24/overlays.html#Referential%20Integrity

Manual page: :man:`slapo-refint(5)`


.. _slapd__ref_auditlog_overlay:

Audit Logging overlay
---------------------

The `auditlog overlay`__ records all changes performed in the LDAP database
using an external log file. Changes are stored in the LDIF format, that
includes a timestamp and the identity of the modifier. The role will
automatically ensure that the audit log files are rotated periodically using
the :command:`logrotate` service to keep the disk usage under control.

.. __: https://www.openldap.org/doc/admin24/overlays.html#Audit%20Logging

Manual page: :man:`slapo-auditlog(5)`


.. _slapd__ref_constraint_overlay:

Attribute Constraints overlay
-----------------------------

The `constraint overlay`__ can be used to place constraints on specific LDAP
attributes, for example number of possible values, size or format.

.. __: https://www.openldap.org/doc/admin24/overlays.html#Constraints

Manual page: :man:`slapo-constraint(5)`


.. _slapd__ref_lastbind_overlay:

LastBind overlay
----------------

The ``lastbind`` overlay and the corresponding OpenLDAP module can be used to
maintain information about last login time of a LDAP account, similar to the
`lastLogon`__ functionality from Active Directory. The primary purpose
of the ``lastbind`` overlay is detection of inactive user accounts; it
shouldn't be relied on for real-time login tracking.

.. __: https://ldapwiki.com/wiki/LastLogon

The time of the last successful authenticated bind operation of a given LDAP
object is stored in the ``authTimestamp`` operational attribute (not
replicated, not visible in normal queries, has to be specifically requested).
By default the timestamp is updated once a day to avoid performance issues in
larger environments.

Manual page: :man:`slapo-lastbind(5)`
