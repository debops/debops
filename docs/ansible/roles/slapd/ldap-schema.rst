.. Copyright (C) 2016-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

.. _slapd__ref_ldap_schemas:

Custom LDAP schemas
===================

The ``debops.slapd`` role by default configures a set of custom LDAP schemas on
top of the default ones enabled during :command:`slapd` installation. The
schemas included in a LDAP directory cannot be removed without issues,
therefore it's best to select the ones you want to use at the database
initialization.

You can find more details about managing the LDAP schemas using ``cn=config``
configuration `in the Zytrax LDAP guide`__.

.. __: http://www.zytrax.com/books/ldap/ch6/slapd-config.html#use-schemas

.. only:: html

   .. contents::
      :local:


General notes
-------------

The ``slapd__*_schemas`` variables define a list of LDAP schemas to import by
the role. The list is not merged via custom Ansible filter plugins and is only
additive. You can define different sets of schemas on different Ansible
inventory levels.

The schema files need to already be present on the remote host to be imported
by the role.

You can use the :ref:`debops.resources` role to copy custom ``*.schema`` or
``*.ldif`` files to the remote host before importing them. The ``*.ldif`` files
can be imported automatically, but the ``*.schema`` import relies on the
:command:`schema2ldif` tool which is available from the APT package with the
same name.

If you are using clustered OpenLDAP, for example in N-Way Multi Master
replication mode, you should import the schemas only on one node at a time.
Execution of the import command on multiple remote hosts at once will result in
an error when one replication host already has a schema defined with a specific
``X-ORDERED`` index number, but the other nodes don't. The schema will be
replicated automatically between all of the OpenLDAP masters.


.. _slapd__ref_rfc2307bis:

The ``rfc2307bis`` schema
-------------------------

The `rfc2307bis LDAP schema`__ is a proposed replacement of the :rfc:`2307`
document that defines the ``nis`` LDAP schema. Main improvement over the old
``nis`` schema is the modified ``posixGroup`` LDAP object, which in the new
schema has an ``AUXILIARY`` type instead of the ``STRUCTURAL`` type. Notably,
the ``posixAccount`` LDAP object has an ``AUXILIARY`` type in the original
``nis`` scheme; the change makes both objects work similarly by allowing an
UNIX-based attributes to be combined with LDAP-based directory entries.

Without this change, LDAP directories that are used in UNIX-like environments
for group authentication require two sets of groups stored in the directory
- one for LDAP entities based on DN attributes, and another for UNIX entities
based on GID attributes. The new schema enables the ``posixGroup`` object
type to combine with other LDAP object types, namely ``groupOfNames`` or
``groupOfUniqueNames``. This allows the two sets of data to be combined in
one object - allowing both the UID and DN attributes to be used as group
members.  This of course depends on the client-side support - both
:command:`nslcd` and :command:`sssd` daemons should be able to use the combined
data sets correctly.

.. __: https://tools.ietf.org/html/draft-howard-rfc2307bis-02

Support in Debian
~~~~~~~~~~~~~~~~~

Some of the Linux-based distributions provide the :command:`slapd` package with
the new ``rfc2307bis`` schema enabled by default. Unfortunately, Debian's
:command:`slapd` APT package includes the original ``nis`` schema which
conflicts with the new ``rfc2307bis`` schema because both define the same LDAP
objects and their attributes. The ``nis`` schema is loaded by default during
the :command:`slapd` package installation and removing it from the already
initialized directory can be difficult.

Fortunately, there's a clean way to avoid this issue and enable the
``rfc2307bis`` schema on :command:`slapd` installation.
Before the installation of the :command:`slapd` APT package, the
``debops.slapd`` role will divert the
:file:`/etc/ldap/schema/nis.(ldif,schema)` files using the
:command:`dpkg-divert` tool, install the ``rfc2307bis`` files to the
:envvar:`slapd__debops_schema_path` directory and create symlinks where the
original ``nis`` schema used to be. With this modification, when the
:command:`slapd` APT package is installed, it will automatically include the
modified ``rfc2307bis`` schema.

The automatic installation of the ``rfc2307bis`` schema can be disabled by
setting the :envvar:`slapd__rfc2307bis_enabled` boolean variable to ``False``.
This allows usage of the LDAP directories that use the old ``nis`` schema
without modifications to the directory contents.


.. _slapd__ref_initial_schemas:

The initial LDAP schemas
------------------------

During installation of the ``slapd`` Debian package, the postinstall script
creates a new OpenLDAP configuration using the
:file:`/usr/share/slapd/slapd.init.ldif` LDIF configuration file. The default
LDAP schemas imported at that time are:

- ``core.schema``
- ``cosine.schema``
- ``nis.schema`` (replaced by the ``rfc2307bis.schema`` before installation)
- ``inetorgperson.schema``

You can find the schema files in the :file:`/etc/ldap/schema/` directory on the
OpenLDAP server host.


.. _slapd__ref_debops_schema:

The ``debops`` schema
---------------------

This schema provides the basic LDAP object identifiers (OIDs) for other LDAP
schemas that are created by DebOps project - the Private Enterprise Number
assigned to the project by IANA and the separate namespace designated to be
used for LDAP schemas. These object identifiers are in a separate "schema" so
that they can be re-used in multiple LDAP schemas imported after this schema
without creating conflicts in the OpenLDAP ``cn=schema`` subtree.


.. _slapd__ref_posixgroupid:

The ``posixgroupid`` schema
---------------------------

This is a custom LDAP schema maintained by DebOps. It can be found in the
:file:`ansible/roles/debops.slapd/files/etc/ldap/schema/debops/` directory of
the DebOps monorepo.

The ``rfc2307bis`` schema fixes one issue with POSIX groups in LDAP - the
``posixGroup`` object attributes can be added to any object type. But there's
one other problem not fixed by this schema - the name of the group is taken
from the ``cn`` attribute. This causes an issue when LDAP group names are in
a human-readable form, instead of a short string form preferred in POSIX
environments, for example: ``UNIX Administrators`` vs ``admins``.

Another issue shows up with different `User Private Group`__ implementations in
LDAP - because the ``cn`` attribute in the LDAP objects that define people is
used for the person's full name, for example "John Smith", personal UNIX groups
cannot be defined in the same LDAP object, even though the ``gidNumber``
attribute is required by the ``posixAccount`` object type.

.. __: https://wiki.debian.org/UserPrivateGroups

There are different solutions to this problem - create a separate
``posixGroup`` object for each person and put it either in a separate directory
subtree, or as a child entry of the person's object, but these solutions are
cumbersome and require hard to implement ACL rules. A different solution is
adding a new attribute that would define the UNIX group name separate from the
common name.

This is what the :file:`posixgroupid.schema` LDAP schema does - it adds the
``gid`` or ``groupid`` attribute, either in a separate ``gidObject`` object
type, or in the ``posixGroupId`` object which is a subclass of the
``posixGroup`` object. With the ``gid`` attribute, LDAP clients that are
configured to use it, can use a different LDAP attribute as the UNIX group name
instead of the human-readable ``cn`` name. Similarly, LDAP objects that
represent people can have a ``gid`` attribute that contains the name of the
Private User Group, usually the same as the ``uid`` attribute. This requires
that the LDAP clients look for the ``gid`` attribute instead of the ``cn``
attribute as the UNIX group name, but it's usually a simple configuration
change.


.. _slapd__ref_nextuidgid_schema:

The ``nextuidgid`` schema
-------------------------

The ``nexuidgid`` schema defines a set of simple LDAP objects (``uidNext``,
``gidNext``), which can be used to store ``uidNumber`` and ``gidNumber``
values, respectively. These objects are used in DebOps to :ref:`keep track of
the next available UID/GID values <ldap__ref_next_uid_gid>`, but can be used
for other purposes, for example to split the UID/GID range used in the LDAP
directory into subranges.


.. _slapd__ref_orgstructure_schema:

The ``orgstructure`` schema
---------------------------

The ``orgstructure`` schema defines an additional LDAP object,
``organizationalStructure``. This object is meant to replace the use of the
``organizationalUnit`` object class in the base LDAP directory entries, such as
``ou=People``, ``ou=Groups``, and so on. The new object contains attributes
selected to help manage the :ref:`access control <slapd__ref_acl>` for specific
LDAP directory subtrees.


.. _slapd__ref_ppolicy_schema:

The ``ppolicy`` schema
----------------------

The ``ppolicy`` schema provides LDAP object and attribute definitions required
by the :ref:`slapd__ref_ppolicy_overlay`.


.. _slapd__ref_ldapns:

The ``ldapns`` schema
---------------------

The ``ldapns`` schema provides a set of LDAP objects and attributes that can be
used for granular access control to services and hosts that use the LDAP
directory. The ``host`` attribute can be used to define a list of FQDN names,
or hostnames to which a given user or application has access. The
``authorizedService`` attribute can contain a list of services accessible to an
user or application. LDAP clients can use these attributes in LDAP filters to
grant access only to specific people or applications.


.. _slapd__ref_groupofentries:

The ``groupofentries`` schema
-----------------------------

The ``groupofentries`` schema defines a new `"groupOfEntries" LDAP Object
Class`__ which is meant to replace the ``groupOfNames`` object defined by
:rfc:`2256`. The new object can be used to create groups that can be empty (no
``member`` attribute required).

.. __: https://tools.ietf.org/html/draft-findlay-ldap-groupofentries-00


.. _slapd__ref_openssh_lpk:

The ``openssh-lpk`` schema
--------------------------

The ``openssh-lpk`` schema allows the LDAP directory to hold SSH public keys,
which combined with OpenSSH ``AuthorizedKeysCommand`` configuration can allow
SSH authentication via LDAP directory. An `example openssh-ldap-publickey`__
script shows how this can be configured with OpenSSH and OpenLDAP.

.. __: https://github.com/AndriiGrytsenko/openssh-ldap-publickey

The :ref:`debops.slapd` Ansible role contains a modified version of the
official schema which adds a separate attribute for the public key
fingerprints, meant to help find the key owners based on the information logged
by the :command:`sshd` service.

The :ref:`debops.sshd` Ansible role already contains support for SSH public key
lookup in OpenLDAP, see its documentation for more details about enabling the
support.

.. _slapd__ref_sudo:

The ``sudo`` schema
-------------------

The `sudo`__ service can be configured to `use LDAP directory as a backend`__
for its rules. The :ref:`debops.sudo` Ansible role will enable the LDAP support
when the :ref:`debops.ldap` configuration is detected (not implemented yet).

.. __: https://en.wikipedia.org/wiki/Sudo
.. __: https://www.sudo.ws/man/1.8.17/sudoers.ldap.man.html

The rules in the LDAP directory are meant to be used with LDAP-based users and
groups; local accounts should still rely on local :file:`/etc/sudoers` contents
to ensure service availability in case of an issue with connection to the LDAP
service.

Manual pages: :man:`sudoers.ldap(5)`

.. _slapd__ref_eduperson:

The ``eduPerson`` schema
------------------------

The ``eduPerson`` and ``eduOrg`` are Lightweight Directory Access Protocol
(LDAP) schema designed to include widely-used person and organizational
attributes in higher education. The ``eduPerson`` object class provides
a common list of attributes and definitions, drawing on the existing standards
in higher education. The schema were developed `by the Internet2 project`__ and
are commonly used in academic institutions.

.. __: https://www.internet2.edu/products-services/trust-identity/eduperson-eduorg/

The version of the schema included in DebOps has been extended with additional
attributes for the ``eduPerson`` and ``eduOrg`` Object Classes not present in
the official specification. These attributes have been found useful in an
academic environment; more attributes might be added in the future if needed.


.. _slapd__ref_schac:

The ``schac`` schema
--------------------

The ``schac`` (`SCHema for ACademia`__) LDAP schema extends the ``eduPerson``
schema with an additional set of LDAP object classes and attributes useful in
university and higher education environments.

.. __: https://wiki.refeds.org/display/STAN/SCHAC


.. _slapd__ref_nextcloud:

The ``nextcloud`` schema
------------------------

The ``nextcloud`` schema provides a set of LDAP objectClasses and attributes
that can be used to control LDAP integration with :ref:`Nextcloud
<debops.owncloud>` application. Using these attributes, administrators can
define disk quotas for Nextcloud users stored in the LDAP directory, as well as
define which user groups present in LDAP are available in the Nextcloud user
interface.

.. _slapd__ref_mailservice:

The ``mailservice`` schema
--------------------------

The ``mailservice`` schema is based on several draft RFCs and includes a set of
LDAP objects and attributes useful for mail services. The ``mailRecipient``
object class provides attributes for "final destination" mail recipient
accounts, like mail aliases, Sieve filtering rules, mail storage location,
quota. The ``mailDistributionList`` object class allows for creation of simple
mailing lists or distribution lists which can be used to distribute e-mail
messages to multiple recipients with basic access controls.

With this schema installed, the ``mail`` attribute should not be used for mail
services, but should be relegated to user authentication only.

.. _slapd__ref_dyngroup:

The ``dyngroup`` schema
-----------------------

The ``dyngroup`` schema provides LDAP object and attribute definitions for
creation of `dynamic groups`__ inside of the LDAP directory. Dynamic group
objects define LDAP search URLs which are resolved by the directory server on
searches and provided to the client with computed set of ``member`` attributes
as opposed to having a static object with members.

In DebOps, this schema is modified by adding the optional ``member`` attribute
to the group objects to support usage of the
:ref:`slapd__ref_autogroup_overlay` which maintains "static" dynamic groups by
updating these objects each time an LDAP entry included in the specified search
is created, modified or destroyed.

.. __: https://www.zytrax.com/books/ldap/ch11/dynamic.html

.. _slapd__ref_freeradius_schema:

The ``freeradius`` schema
-------------------------

The ``freeradius`` schema provide definitions of various LDAP objects usable by
the `FreeRADIUS`__ service, namely RADIUS Clients, RADIUS Profiles, RADIUS
Accounting database objects, and FreeRADIUS DHCPv4/DHCPv6 configuration
objects. The version of the schema included in DebOps is based on the
``master`` branch of the FreeRADIUS project code.

Keep in mind that the FreeRADIUS schema is split into multiple
:file:`freeradius-*.schema` files, and the main file defines just the
``objectIdentifier`` LDAP objects used in other schema files. If you don't want
to use specific FreeRADIUS features you should be able to disable them by
changing the list of LDAP schemas the role loads, but the
:file:`freeradius.schema` file should be always present.

.. __: https://freeradius.org/
