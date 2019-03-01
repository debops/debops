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

.. contents::
   :local:


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
``rfc2307bis`` schema on :command:`slapd` installation. The Debian Archive
contains two packages that provide it: `fusiondirectory-schema`__ and
`gosa-schema`__. Both packages conflict with each other, therefore only one can
be installed at a time. In the ``debops.slapd`` role, the
``fusiondirectory-schema`` has been selected because FusionDirectory project
seems to be an actively maintained fork of GOsa² and will be more likely to be
selected for installation; another reason is more
``fusiondirectory-plugin-*-schema`` APT packages available in Debian.

The role still works fine with ``gosa-schema`` APT package installed, however
this will not be detected automatically; the user should redefine the
:envvar:`slapd__rfc2307bis_packages` list the Ansible inventory to select this
APT package.

.. __: https://packages.debian.org/stable/fusiondirectory-schema
.. __: https://packages.debian.org/stable/gosa-schema

Before the installation of the :command:`slapd` APT package, the
``debops.slapd`` role will install the ``fusiondirectory-schema`` package,
divert the :file:`/etc/ldap/schema/nis.(ldif,schema)` files aside using the
:command:`dpkg-divert` tool and create a symlink to the
:file:`/etc/ldap/fusiondirectory/rfc2307bis.(ldif,schema)` files in their
place. With this modification, when the :command:`slapd` APT package is
installed, it will automatically include the modified ``rfc2307bis`` schema.

The automatic installation of the ``rfc2307bis`` schema can be disabled by
setting the :envvar:`slapd__rfc2307bis_enabled` boolean variable to ``False``.
This allows usage of the LDAP directories that use the old ``nis`` schema
without modifications to the directory contents.
