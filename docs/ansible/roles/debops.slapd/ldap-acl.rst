.. _slapd__ref_acl:

LDAP Access Control List
========================

The default Access Control List is defined in the :envvar:`slapd__acl_tasks`
default variable. It might be preferable to override this variable in the
Ansible inventory by copying its contents there. This should keep the existing
ACL rules intact in case of any updates to the :ref:`debops.slapd` role.

The default ACL will be updated over time when new DebOps roles are integrated
with the LDAP directory. The DebOps documentation contains a :ref:`browseable
representation of the LDAP Directory Information Tree <slapd__ref_ldap_dit>`
that maps how various DebOps roles interact with the directory; this should
enable easier redesign of the Access Control List according to the needs of
one's organization.

You can use the :file:`ansible/playbooks/ldap/init-directory.yml` Ansible
playbook to initialize the new LDAP directory with the objects designed with
the default ACL in mind. See :ref:`ldap__ref_ldap_init` for more details.

.. contents::
   :local:


Default security policy
-----------------------

- Deny anonymous access, apart from authentication to the LDAP directory.

- Define access for groups of LDAP objects, not for specific objects.

- Nobody but LDAP administrators and replicators should be able to read
  ``userPassword`` attribute values, but replacement should be possible.

- Grant LDAP administrators full access to the LDAP directory, including
  passwords and confidential information.

- Grant LDAP replicators read-only access to entire LDAP directory, including
  passwords and other confidential data (required for full replication).

- Treat UNIX/POSIX environment as separate security domain, with its own group
  of administrators that can define UID/GID values and other attributes related
  to it.

- Grant LDAP editors write access to most of the LDAP directory. They don't
  have write access to ``ou=System Groups`` subtree as well as to the UNIX
  attributes, they cannot see passwords (but can change them).

- Group owners should be able to add or remove members of their own group.

- Object owners should be able to modify passwords in their own objects.

- Authenticated users should have read access to most of the directory, apart
  from security-sensitive data like passwords or private keys.


Required LDAP schemas
---------------------

These LDAP schemas are expected to be present in the LDAP directory by the
default ACL rules:

- ``rfc2307bis``
- ``posixgroupid``

If some of the schemas specified here are not present, the default ACL
configuration will not be enabled correctly.


Important Distinguished Names
-----------------------------

This section of the documentation lists various LDAP objects that can be
present in the LDAP directory and are included in the ACL. They might not be
present initially and might need to be created by the administrator to perform
their function. The LDAP Distinguished Names used in the documentation assume
that the ``example.org`` DNS domain is used by the OpenLDAP server.

.. _slapd__ref_acl_dn_ldap_admins:

cn=LDAP Administrators,ou=System Groups,dc=example,dc=org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a ``groupOfNames`` LDAP object that defines via its ``member``
attribute the Distinguished Names of the people who have full, privileged
access to the LDAP directory.

.. _slapd__ref_acl_dn_ldap_replicators:

cn=LDAP Replicators,ou=System Groups,dc=example,dc=org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The is a ``groupOfNames`` LDAP object that defines via its ``member`` attribute
the Distinguished Names of the objects that are used for authenticated access
to data replication by other OpenLDAP servers. This group should have full
access to the LDAP directory for successful replication.

.. _slapd__ref_acl_dn_unix_admins:

cn=UNIX Administrators,ou=System Groups,dc=example,dc=org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a ``groupOfNames`` LDAP object that defines via its ``member``
attribute the Distinguished Names of the UNIX administrators. These accounts
will be able to manipulate the LDAP attributes of certain objects
(``posixAccount``, ``posixGroup``, ``posixGroupId``) which can affect the
security boundary in an UNIX-like environment.

.. _slapd__ref_acl_dn_ldap_editors:

cn=LDAP Editors,ou=System Groups,dc=example,dc=org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a ``groupOfNames`` LDAP object that defines via its ``member``
attribute the Distinguished Names of the LDAP editors. The editors are expected
to be proficient in LDAP management and are granted write access to most of the
LDAP directory, apart from the ``ou=System Groups`` subtree and UNIX
attributes.

.. _slapd__ref_acl_dn_account_admins:

cn=Account Administrators,ou=System Groups,dc=example,dc=org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a ``groupOfNames`` LDAP object that defines via its ``member``
attribute the Distinguished Names of the account administrators. They are
responsible for managing the user accounts of people, client machines,
organizational groups and other user-specific data.

.. _slapd__ref_acl_dn_password_reset:

cn=Password Reset Agents,ou=System Groups,dc=example,dc=org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a ``groupOfNames`` LDAP object that defines via its ``member``
attribute the Distinguished Names of the Password Reset Agents, usually
application(s) that act on behalf of the users to allow them to perform
password changes after out-of-band authentication. This group should have
access to user passwords to be able to reset them.


Access Control List rules
-------------------------

This section of the documentation contains human-readable explanation of the
ACL rules defined in the :envvar:`slapd__acl_tasks` default variable. These
rules should be kept up to date with changes to the ACL contents.


.. _slapd__ref_acl_rule0:

Rule 0: full access by LDAP admins and replicators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: main LDAP directory tree
:Manage by: :ref:`slapd__ref_acl_dn_ldap_admins`
:Read by:   :ref:`slapd__ref_acl_dn_ldap_replicators`
:Others:    continue evaluation

- Grant full access to the entire LDAP directory tree by the members of the
  :ref:`slapd__ref_acl_dn_ldap_admins` group, including passwords and other
  confidential data.

- Grant read-only access to the entire LDAP directory tree by the members of
  the :ref:`slapd__ref_acl_dn_ldap_replicators` group, including passwords and
  other confidential data.

- Continue evaluation of the ACL rules for anyone else.

.. note::
   LDAP administrators and replicator accounts should have full access to the
   entire LDAP directory.


.. _slapd__ref_acl_rule1:

Rule 1: restrict access to POSIX attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: POSIX objects with specific attributes
:Write by:  UNIX Administrators
:Read by:   authenticated users

- Grant write access to the ``uid``, ``uidNumber``, ``gid``, ``gidNumber`` and
  ``homeDirectory`` attributes in ``posixAccount``, ``posixGroup`` and
  ``posixGroupId`` LDAP objects by the members of the
  :ref:`slapd__ref_acl_dn_unix_admins` group.

- Authenticated users can read contents of the specific POSIX attributes, but
  not modify them.

.. note::
   The POSIX/UNIX environment is treated as a separate security domain with its
   own rules, different than the LDAP directory domain. Only a specific subset
   of UNIX administrators should be able to manage this security domain.


.. _slapd__ref_acl_rule2:

Rule 2: restrict access to shadow database of the personal accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to:     ``shadowLastChange`` attribute in personal accounts
:Write by:      object owners (self), LDAP Editors, Account Administrators
:Write-only by: Password Reset Agents
:Read by:       authenticated users

- Grant write access to the ``shadowLastChange`` attribute in all objects under
  the ``ou=People,dc=example,dc=org`` Distinguished Name by the object owners
  (self) to allow for password changes by the users themselves.

- Grant write access to the ``shadowLastChange`` attribute in all objects under
  the ``ou=People,dc=example,dc=org`` Distinguished Name by the members of the
  :ref:`slapd__ref_acl_dn_ldap_editors` and
  :ref:`slapd__ref_acl_dn_account_admins` groups.

- Grant write-only access to the ``shadowLastChange`` attribute in all objects
  under the ``ou=People,dc=example,dc=org`` Distinguished Name by the members
  of the :ref:`slapd__ref_acl_dn_password_reset` group to allow successfull
  password resets.

- Grant read-only access to the ``shadowLastChange`` attribute in all objects
  under the ``ou=People,dc=example,dc=org`` Distinguished Name by the
  authenticated users.

.. note::
   This rule is required for successful password changes performed by the
   object owners and other entities that are allowed to set new passwords or
   change existing ones.


.. _slapd__ref_acl_rule3:

Rule 3: restrict access to password attribute of the personal accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to:     ``userPassword`` attribute in personal accounts
:Write-only by: object owners (self), LDAP Editors, Account Administrators,
                Password Reset Agents
:Auth by:       anonymous users
:Others:        no access

- Grant write-only access to the ``userPassword`` attribute in all objects
  under the ``ou=People,dc=example,dc=org`` Distinguished Name by the object
  owners (self) to allow for password changes by the users themselves.

- Grant write-only access to the ``userPassword`` attribute in all objects
  under the ``ou=People,dc=example,dc=org`` Distinguished Name by the members
  of the :ref:`slapd__ref_acl_dn_ldap_editors`,
  :ref:`slapd__ref_acl_dn_account_admins` and
  :ref:`slapd__ref_acl_dn_password_reset` groups.

- Permit authentication attempts using the ``userPassword`` attribute in all
  objects under the ``ou=People,dc=example,dc=org`` Distinguished Name by the
  anonymous users.

- Deny access to the ``userPassword`` attribute in all objects under the
  ``ou=People,dc=example,dc=org`` Distinguished Name to everyone else.

.. note::
   This rule is required for successful user account password changes performed
   by the object owners and other entities that are allowed to set new
   passwords or change existing ones, and to allow authentication by anonymous
   users. Hashed password strings should not be available to unprivileged users
   to limit brute-force attempts.


.. _slapd__ref_acl_rule4:

Rule 4: restrict access to password attribute in LDAP directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to:     ``userPassword`` attribute in all objects
:Write-only by: object owners (self)
:Auth by:       anonymous users
:Others:        no access

- Grant write-only access to the ``userPassword`` attribute in all objects in
  the LDAP directory  by the object owners (self) to allow for password changes
  by the users themselves.

- Permit authentication attempts using the ``userPassword`` attribute in all
  objects in the LDAP directory by the anonymous users.

- Deny access to the ``userPassword`` attribute in all objects in the LDAP
  directory to everyone else.

.. note::
   This rule is required for successful password changes performed by the
   object owners and to allow authentication by anonymous users. Hashed
   password strings should not be available to unprivileged users to limit
   brute-force attempts.


.. _slapd__ref_acl_rule5:

Rule 5: restrict access to System Groups by LDAP editors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to:    objects under the ``ou=System Groups,dc=example,dc=org`` DN
:Read-only by: LDAP Editors
:Others:       continue evaluation

- Grant read-only access to all objects under the ``ou=System
  Groups,dc=example,dc=org`` Distinguished Name by the members of the
  :ref:`slapd__ref_acl_dn_ldap_editors` group.

- Continue evaluation of the ACL rules for anyone else.

.. note::
   The objects under the ``ou=System Groups,dc=example,dc=org`` Distinguished
   Name are used to control privileged access to the LDAP directory and other
   security contexts. LDAP Editors should not be allowed to modify them,
   otherwise they could easily grant themselves more privileged access.


.. _slapd__ref_acl_rule6:

Rule 6: write access to most of the directory by LDAP editors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: most sections of the main LDAP directory tree
:Write by:  :ref:`slapd__ref_acl_dn_ldap_editors`
:Others:    continue evaluation

- Grant write access to the most parts of the main LDAP directory tree by the
  members of the :ref:`slapd__ref_acl_dn_ldap_editors` group.

- Continue evaluation of the ACL rules for anyone else.

.. note::
   The LDAP Editors have write access to the entire LDAP directory tree, apart
   from the restrictions set in the previous ACL rules.


.. _slapd__ref_acl_rule7:

Rule 7: group owners can add or remove members of their groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: ``member`` attribute of the ``System Groups`` or ``Groups`` LDAP
            objects
:Write by:  owners of a given group
:Others:    continue evaluation

- Grant write access to the ``member`` attribute of the child objects under the
  ``ou=System Groups,dc=example,dc=org`` or ``ou=Groups,dc=example,dc=org``
  Distinguished Names by the accounts defined in the ``owner`` attribute of
  a given child object.

- Continue evaluation of the ACL rules for anyone else.

.. note::
   The owners of the groups defined under the ``ou=System
   Groups,dc=example,dc=org`` or ``ou=Groups,dc=example,dc=org`` Distinguished
   Names should be able to add or remove members in their own group.


.. _slapd__ref_acl_rule8:

Rule 8: account admins can create new child objects under specific DNs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: new child objects of specific Distinguished Names
:Write by:  :ref:`slapd__ref_acl_dn_account_admins`
:Others:    continue evaluation

- Grant write access to new children objects and the entries of the
  ``ou=People,dc=example,dc=org``, ``ou=Machines,dc=example,dc=org`` and
  ``ou=Groups,dc=example,dc=org`` Distinguished Names by the members of the
  :ref:`slapd__ref_acl_dn_account_admins` group.

- Continue evaluation of the ACL rules for anyone else.

.. note::
   Account administrators should be able to add new user and client machine
   accounts, as well as create new groups in the LDAP directory. Access to the
   parent objects themselves is granted only when children are specified, to
   allow creation of new children objects.


.. _slapd__ref_acl_rule9:

Rule 9: account admins can modify existing child objects under specific DNs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: existing child objects of specific Distinguished Names
:Write by:  :ref:`slapd__ref_acl_dn_account_admins`
:Others:    continue evaluation

- Grant write access to existing children objects of the
  ``ou=People,dc=example,dc=org``, ``ou=Machines,dc=example,dc=org`` and
  ``ou=Groups,dc=example,dc=org`` Distinguished Names by the members of the
  :ref:`slapd__ref_acl_dn_account_admins` group.

- Continue evaluation of the ACL rules for anyone else.

.. note::
   Account administrators should be able to modify user and client machine
   accounts, as well as modify existing groups in the LDAP directory.


.. _slapd__ref_acl_rule10:

Rule 10: grant read access to authenticated users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Access to: entire LDAP directory
:Read by:   authenticated users
:Others:    no access

- Grant read access to entire LDAP directory by authenticated users.

- Deny access to all objects in the LDAP directory to everyone else.

.. note::
   Authenticated users should be able to read contents of the LDAP directory,
   apart from any restrictions imposed by earlier ACL rules.


Current issues with the default ACL
-----------------------------------

- LDAP editors and account administrators can modify or remove accounts of the
  LDAP administrators, thus denying access to the service. There should be
  a way to protect certain user objects based on the ``member`` attribute of
  a specific ``groupOfNames`` LDAP object.

- users can create new LDAP objects with object classes or attributes that they
  don't have access to (for example, UNIX attributes). There should be
  a server-side way to restrict object creation to allowed object classes only.


References
----------

- `OpenLDAP Access Control`__ documentation

  .. __: https://www.openldap.org/doc/admin24/access-control.html

- `OpenLDAP-DIT`__ page on Ubuntu Wiki, along with the `project page`__ on
  Launchpad

  .. __: https://wiki.ubuntu.com/OpenLDAP-DIT
  .. __: https://launchpad.net/openldap-dit

- `Keeping your sanity while designing LDAP ACLs`__

  .. __: https://medium.com/@moep/keeping-your-sanity-while-designing-openldap-acls-9132068ed55c

- `Basic ACL configuration`__ in Zytrax LDAP guide

  .. __: http://www.zytrax.com/books/ldap/ch5/step2.html#step2
