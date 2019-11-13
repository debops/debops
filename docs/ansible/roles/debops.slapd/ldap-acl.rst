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
  have write access to the LDAP Administrators and the LDAP Replicators roles,
  the UNIX Administrators group, the ``ou=System Groups`` subtree as well as to
  the UNIX attributes, they cannot see passwords (but can change them).

- Group owners should be able to add or remove members of their own group.

- Object owners should be able to modify passwords in their own objects.

- Authenticated users should have read access to most of the directory, apart
  from security-sensitive data like passwords or private information.


Required LDAP schemas
---------------------

These LDAP schemas are expected to be present in the LDAP directory by the
default ACL rules:

- ``rfc2307bis``
- ``posixgroupid``

If some of the schemas specified here are not present, the default ACL
configuration will not be enabled correctly.


Directory groups
----------------

In this section of the documentation you can find a list of LDAP groups which
are used in the default :ref:`debops.slapd` Access Control List rules. These
groups can be created in the directory using the
:file:`ldap/init-directory.yml` Ansible playbook included in DebOps. The LDAP
Distinguished Names used in the documentation assume that the ``example.org``
DNS domain is used by the OpenLDAP server.

The "Test RDN" and "Test DN" attributes refer to the
:ref:`slapd__ref_acl_tests` and specifically to the
:envvar:`slapd__slapacl_test_rdn_map` variable.

.. _slapd__ref_acl_group_unix_admins:

UNIX Administrators
~~~~~~~~~~~~~~~~~~~

:DN:       cn=UNIX Administrators,ou=Groups,dc=example,dc=org
:Test RDN: ``unix_admin_rdn``
:Obsolete: cn=UNIX Administrators,ou=System Groups,dc=example,dc=org

- Members of this group have write access to the ``uid``, ``uidNumber``,
  ``gid``, ``gidNumber`` and ``homeDirectory`` attributes of the
  ``posixAccount``, ``posixGroup`` and ``posixGroupId`` LDAP objects. Everyone
  else has read-only access to these attributes.

- Members of this group have write access to the
  ``ou=SUDOers,dc=example,dc=org`` LDAP subtree which contains
  :man:`sudoers.ldap(5)` configuration. Everyone else has read-only access.

- Access to the group is restricted to Read-only by role occupants of the
  :ref:`slapd__ref_acl_role_ldap_editor` and the
  :ref:`slapd__ref_acl_role_account_admin` LDAP roles.

.. _slapd__ref_acl_group_hidden_objects:

Hidden Objects
~~~~~~~~~~~~~~

:DN: cn=Hidden Objects,ou=Groups,dc=example,dc=org

- Objects in this group are visible only to themselves as well as people and
  other entities with the :ref:`slapd__ref_acl_role_ldap_admin`, the
  :ref:`slapd__ref_acl_role_ldap_editor` and the
  :ref:`slapd__ref_acl_role_hidden_object_viewer` roles.

- The access control list checks the ``memberOf`` attribute of an LDAP object
  and grants or denies access to it depending on its membership status.

.. note:: Due to limitations of the OpenLDAP Access Control List features, to
   hide the children objects of a given LDAP object, all of them need to be
   also included as separate ``member`` attributes in the
   :ref:`slapd__ref_acl_group_hidden_objects` group. Otherwise the children of
   hidden objects can be still visible in general LDAP searches, for example
   ``(objectClass=*)``. The DN attribute of such entries can also disclose the
   presence of a hidden object.


Directory roles
---------------

In this section of the documentation you can find a list of LDAP roles which
are used in the default :ref:`debops.slapd` Access Control List rules. These
roles can be created in the directory using the :file:`ldap/init-directory.yml`
Ansible playbook included in DebOps. The LDAP Distinguished Names used in the
documentation assume that the ``example.org`` DNS domain is used by the
OpenLDAP server.

The "Test RDN" and "Test DN" attributes refer to the
:ref:`slapd__ref_acl_tests` and specifically to the
:envvar:`slapd__slapacl_test_rdn_map` variable.

.. _slapd__ref_acl_role_ldap_admin:

LDAP Administrator
~~~~~~~~~~~~~~~~~~

:DN:       cn=LDAP Administrator,ou=Roles,dc=example,dc=org
:Test RDN: ``ldap_admin_rdn``
:Obsolete: cn=LDAP Administrators,ou=System Groups,dc=example,dc=org

- Role grants full access to the entire LDAP directory.

- Access to the role is restricted to read-only by role occupants of the
  :ref:`slapd__ref_acl_role_ldap_editor` and the
  :ref:`slapd__ref_acl_role_account_admin` LDAP roles.

.. _slapd__ref_acl_role_ldap_replicator:

LDAP Replicator
~~~~~~~~~~~~~~~

:DN:       cn=LDAP Replicator,ou=Roles,dc=example,dc=org
:Test DN:  ``ldap_replicator_dn``
:Obsolete: cn=LDAP Replicators,ou=System Groups,dc=example,dc=org

- Role grants read-only access to the entire LDAP directory.

- Access to the role is restricted to read-only by role occupants of the
  :ref:`slapd__ref_acl_role_ldap_editor` and the
  :ref:`slapd__ref_acl_role_account_admin` LDAP roles.

.. _slapd__ref_acl_role_ldap_editor:

LDAP Editor
~~~~~~~~~~~

:DN:       cn=LDAP Editor,ou=Roles,dc=example,dc=org
:Test RDN: ``ldap_editor_rdn``
:Obsolete: cn=LDAP Editors,ou=System Groups,dc=example,dc=org

- Role grants write access to most of the LDAP directory, apart from the
  privileged groups and roles.

.. _slapd__ref_acl_role_account_admin:

Account Administrator
~~~~~~~~~~~~~~~~~~~~~

:DN:       cn=Account Administrator,ou=Roles,dc=example,dc=org
:Test RDN: ``account_admin_rdn``
:Obsolete: cn=Account Administrators,ou=System Groups,dc=example,dc=org

- Role grants write access to the ``shadowLastChange`` and write-only access to
  the ``userPassword`` attributes in the ``ou=People,dc=example,dc=org`` LDAP
  subtree to allow password changes in personal accounts.

- Role grants write access in the ``ou=People,dc=example,dc=org``,
  ``ou=Groups,dc=example,dc=org`` and the ``ou=Machines,dc=example,dc=org``
  LDAP subtrees.

.. note:: Purpose of this role is too broad and in the future it will be split
   into separate, more focused LDAP roles.

.. _slapd__ref_acl_role_password_reset:

Password Reset Agent
~~~~~~~~~~~~~~~~~~~~

:DN:       cn=Password Reset Agent,ou=Roles,dc=example,dc=org
:Test DN: ``password_reset_dn``
:Obsolete: cn=Password Reset Agents,ou=System Groups,dc=example,dc=org

- Role grants write-only access to the ``shadowLastChange`` and the
  ``userPassword`` attributes in the ``ou=People,dc=example,dc=org`` LDAP
  subtree to allow password changes in personal accounts.

- This role is meant for applications that act on behalf of the users to allow
  them to perform password changes after out-of-band authentication.

.. _slapd__ref_acl_role_sms_gateway:

SMS Gateway
~~~~~~~~~~~

:DN:       cn=SMS Gateway,ou=Roles,dc=example,dc=org
:Test DN: ``sms_gateway_dn``

- Role grants read-only access to the ``mobile`` LDAP attribute, required by
  the SMS gateways to send SMS messages.

.. _slapd__ref_acl_role_hidden_object_viewer:

Hidden Object Viewer
~~~~~~~~~~~~~~~~~~~~

:DN: cn=Hidden Object Viewer,ou=Roles,dc=example,dc=org

- Role occupants can see LDAP objects included in the
  :ref:`slapd__ref_acl_group_hidden_objects` LDAP group.


Other directory objects
-----------------------

This section of the documentation describes various other LDAP objects and
their default access policy defined by the :ref:`debops.slapd` Ansible role.

System Groups
~~~~~~~~~~~~~

:DN: ou=System Groups,dc=example,dc=org

- This subtree was used to hold LDAP objects related to access control, which
  have been converted to normal groups and roles. It can be safely removed from
  existing LDAP directories; the ACL rules for this LDAP object will be removed
  at a later date to allow for secure migration to the new directory layout.

Group owners
~~~~~~~~~~~~

- The owners of the LDAP groups under the ``ou=Groups,dc=example,dc=org`` LDAP
  subtree, defined by the ``owner`` attribute, can add, modify or remove
  members in their respecitve groups, using the ``member`` attribute.

Object owners
~~~~~~~~~~~~~

:DN: self

- Object owners see their own LDAP objects even if they are hidden using the
  :ref:`slapd__ref_acl_group_hidden_objects` LDAP group.

- Object owners have write access to the ``shadowLastChange`` attribute, and
  write-only access to the ``userPassword`` attribute in their own LDAP objects
  to allow password changes.

- Object owners have write access to the ``mobile``, ``carLicense``,
  ``homePhone`` and ``homePostalAddress`` attributes in their own objects.
  These attributes cannot be seen by other unprivileged users.

Authenticated users
~~~~~~~~~~~~~~~~~~~

:DN: users
:Test RDN: ``person_rdn``

- Authenticated users have read-only access to most of the LDAP directory,
  depending on the restrictions defined by the ACL rules.

Anonymous users
~~~~~~~~~~~~~~~

:DN: anonymous

- Anonymous users can authenticate to the LDAP directory via the
  ``userPassword`` attribute.

- No other access is granted to anonymous users.


Current issues with the default ACL
-----------------------------------

- LDAP editors and account administrators can modify or remove accounts of the
  LDAP administrators, thus denying access to the service. There should be
  a way to protect certain user objects based on the ``member`` attribute of
  a specific ``groupOfNames`` LDAP object.

- users can create new LDAP objects with object classes or attributes that they
  don't have access to (for example, UNIX attributes). There should be
  a server-side way to restrict object creation to allowed object classes only.


.. _slapd__ref_acl_tests:

Access Control List tests and validation
----------------------------------------

Due to its complexity, LDAP access control policy requires extensive testing to
ensure that there are no missed loopholes or unintended data disclosures. With
OpenLDAP service, the :man:`slapacl(8)` command can be used to test the ACL
rules against existing or simulated LDAP objects.

The :command:`slapacl` command has to be executed with full access to the
``cn=config`` database, which means running it on the OpenLDAP server itself,
as the ``openldap`` UNIX account. Unfortunately, :command:`slapacl` command
does not support any test definition files and the tests have to be applied
using command line arguments.

To make ACL testing more reliable and easier to use, the :ref:`debops.slapd`
Ansible role implements a custom template and :ref:`a set of variables
<slapd__ref_slapacl_tests>` which can be used to generate a shell script, by
default located at :file:`/etc/ldap/slapacl-test-suite`. This script can then
be executed to perform various ACL tests and report the results. The test suite
is executed by Ansible on each run of the :ref:`debops.slapd` role to ensure
that any changes to the ACL rules are immediately tested.

.. warning:: The test suite shell script is executed by Ansible as the
   ``openldap`` UNIX account and has full access to the OpenLDAP environment,
   database and other files owned by the service. The generated test cases are
   not validated against any command injection attacks through the Ansible
   variables and could be used to take over the OpenLDAP service. Ensure that
   the access to the OpenLDAP servers and the Ansible inventory used to
   configure them is restricted.

To generate the test suite script and perform the tests using Ansible, you can
execute the :ref:`debops.slapd` playbook with a special tag:

.. code-block:: console

   debops service/slapd -l <host> -t role::slapd:slapacl

This command will regenerate the script and execute it to check the ACL rules.

The test script is designed with a large number of ACL test cases in mind
(200+). By default it only outputs the details about failed test cases, to make
them easier to spot on the command line, or in Ansible output. To see the full
report of the various tests, you need to redirect the standard output to
another command, for example:

.. code-block:: console

   /etc/ldap/slapacl-test-suite | more

The output of the failed test cases is sent to the standard error. You can
redirect the failed test cases to a file for further analysis:

.. code-block:: console

   /etc/ldap/slapacl-test-suite 2> /tmp/slapd-acl-errors

In this case the script will print the ``.`` to indicate successful tests and
``X`` for failed tests on its standard output.

The :envvar:`default set of test cases <slapd__slapacl_default_tests>` is
designed to test validity of the default LDAP Access Control List rules defined
by the :ref:`debops.slapd` role and will be expanded over time to cover more
test cases. If you modify the default ACL rules, you might also need to update
the existing test cases to conform to the new rules. Alternatively, the
execution of the test script by Ansible :envvar:`can be disabled
<slapd__slapacl_run_tests>` temporarily or permanently if you don't want your
new ACL rules to fail the Ansible execution during development.

Some of the test cases require real, existing LDAP objects to execute properly.
The :ref:`debops.slapd` role provides the :envvar:`slapd__slapacl_test_rdn_map`
YAML dictionary that contains Relative Distinguished Names of various LDAP
objects like unprivileged and privileged user accounts. To enable the more
extensive tests, you need to create the required LDAP objects, grant them the
permissions you want and define their Relative Distinguished Names in the above
YAML dictionary through the Ansible inventory. When the default values of the
variable are changed, the role will enable the additional tests automatically.


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
