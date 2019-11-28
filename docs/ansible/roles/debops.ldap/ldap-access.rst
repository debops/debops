.. _ldap__ref_ldap_access:

LDAP Access Control
===================

The Lightweight Directory Access Protocol is commonly used to implement access
control policies in organizations. Various methods are available, from
`Mandatory Access Control (MAC)`__ policy which can define directly what
entities have access to which services, through the `Role-Based Access Control
(RBAC)`__ scheme which can be used to grant different levels of access to
different entities.

.. __: https://en.wikipedia.org/wiki/Mandatory_access_control
.. __: https://en.wikipedia.org/wiki/Role-based_access_control

This document describes various mechanisms which are available in the DebOps
LDAP environment supported by the :ref:`debops.ldap` and :ref:`debops.slapd`
Ansible roles. These mechanisms can be used in different services to implement
access control to a varying degree, based on the application.

.. note:: Not all rules defined here are implemented in various DebOps roles at
          the moment.


Controlling access to LDAP objects in the directory
---------------------------------------------------

The :ref:`debops.slapd` role implements a default :ref:`slapd__ref_acl` which
can be used to define which LDAP objects have access to data and at what level.
By default, read access is granted to almost entire LDAP directory by
authorized users; role-based and group-based access control is used to limit
read and/or write access to specific LDAP attributes.


Account-based access control
----------------------------

Applications can use the LDAP bind operation to check if a given username and
password combination is valid. To accomplish that, applications can utilize
either a Distinguished Name provided by the user, match the username to
a personal LDAP entry with the ``uid`` attribute stored in
``ou=People,dc=example,dc=org`` directory subtree, or use a search query to
find the LDAP entry of a person or a service account in the LDAP directory
using their username (in the ``uid`` attribute) or the provided e-mail address
(in the ``mail`` attribute). After finding the correct Distinguished Name,
applications need to privde the plaintext password over the TLS connection to
the LDAP directory which will then verify it and confirm the validity.
Successful bind operations should grant access to the application.

This access method is good for services and applications which should be
available to all legitimate users in an organization. Anonymous and external
users will not be granted access without authenticating first.

Various applications also require their own account objects in the LDAP
directory to access its contents. These accounts are usually stored under the
host objects in the ``ou=Hosts,dc=example,dc=org`` LDAP subtree, or if the
applications are external to the organization or are implemented as a cluster,
under the ``ou=Services,dc=example,dc=org`` LDAP subtree. Application accounts
are subject to the LDAP Access Control List rules defined by the OpenLDAP
service and may not have access to all of the LDAP entries and/or attributes.

This authorization type is global - any LDAP entry with ``userPassword``
attribute can be used to authorize access to a resource.

Examples of LDAP search queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Directly check existence of a LDAP entry:

.. code-block:: console

   ldapsearch -Z -b "uid=$value,ou=People,dc=example,dc=org" uid

Search for personal Distinguished Name based on username or e-mail address.
Esure that only one LDAP entry is returned, more entries result in an error
code from LDAP which needs to be handled by the application:

.. code-block:: console

   ldapsearch -Z -z 1 -b ou=People,dc=example,dc=org \
              "(& (objectClass=inetOrgPerson) (| (uid=$value) (mail=$value) ) )" dn

Search for service account Distinguished Name based on username and FQDN of the
host. Only one LDAP entry is allowed, more entries should result in an error:

.. code-block:: console

   ldapsearch -Z -z 1 -b dc=example,dc=org \
              "(& (objectClass=account) (uid=$username) (host=$fqdn) )" dn


Access control based on group membership
----------------------------------------

The group LDAP objects, defined under the ``ou=Groups,dc=example,dc=org`` LDAP
subtree, can be used to control access to resources. These objects usually use
the ``groupOfNames`` object class with the ``member`` attribute which defines
the group members. Optionally, these objects can define a corresponding POSIX
group using the ``posixGroup`` and ``posixGroupId`` object classes which can
then be used to define access control in an UNIX environment.

The ``groupOfNames`` object class enforces at least one group member at all
times. Groups can also have defined owners or managers using the ``owner``
attribute; in the default :ref:`slapd__ref_acl` configuration group owners have
the ability to add or remove group members from the groups they own.

Applications can check the ``member`` attribute of one or more groups to
determine if a given user or application account belongs to a group and with
that information grant or revoke access to resources. Alternatively, the
``memberOf`` attribute of the user or account LDAP object can be used to
determine group membership and control resource access based on that
information.

This authorization type can be either global, or scoped to a particular
application with group entries located under the ``ou=Groups`` subtree under
the application LDAP entry.

Examples of LDAP search queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the Distinguished Names of LDAP entries which are members of the
:ref:`slapd__ref_acl_group_unix_admins` group:

.. code-block:: console

   ldapsearch -Z -b "cn=UNIX Administrators,ou=Groups,dc=example,dc=org" member

Get the list of group Distinguished Names a given user belongs to:

.. code-block:: console

   ldapsearch -Z -b "uid=$username,ou=People,dc=example,dc=org" memberOf

Find all members of the :ref:`slapd__ref_acl_group_unix_admins` group:

.. code-block:: console

   ldapsearch -Z "(memberOf=cn=UNIX Administrators,ou=Groups,dc=example,dc=org)" dn


Role-based access control
-------------------------

The role LDAP objects, defined under the ``ou=Roles,dc=example,dc=org`` LDAP
subtree, are similar to the group objects described above. They are usually
defined using the ``organizationalRole`` object class, and use the
``roleOccupant`` attribute to determine the people and accounts which are
granted a given role.

The ``organizationalRole`` object class does not require any particular members
to be present, unlike the ``groupOfNames`` object class. This is a good choice
to create various roles which don't have existing role occupants - different
roles can then be granted to different people or accounts at a later date.

This authorization type can be either global, or scoped to a particular
application with role entries located under the ``ou=Roles`` subtree under the
application LDAP entry.

Examples of LDAP search queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get the Distinguished Names of LDAP entries which are included in the
:ref:`slapd__ref_acl_role_ldap_admin` role:

.. code-block:: console

   ldapsearch -Z -b "cn=LDAP Administrator,ou=Roles,dc=example,dc=org" roleOccupant


Attribute-based access control
------------------------------

LDAP entries can include the ``authorizedServiceObject`` object class which
provides the ``authorizedService`` attribute. This attribute is a multi-valued
string which can be used to define the access permissions to a particular
resource. Only "equal" match for this attribute is defined in the LDAP schema,
which limits its capabilities to a degree - searching for partial string
matches is not supported.

This authorization type is scoped to an LDAP entry, which results in less LDAP
queries needed to find out particular access permissions. It can be used to
implement `Attribute-Based Access Control (ABAC)`__ authorization scheme.

.. __: https://en.wikipedia.org/wiki/Attribute-based_access_control

In DebOps, applications should standardize on a structured format of the
attribute values, either ``all``, ``<service>``, ``<system>``, or
``<system>:<type>``.

Global permissions
~~~~~~~~~~~~~~~~~~

The ``all`` value grants access to all services and systems and if present,
should be the only value of the ``authorizedService`` attribute. Any additional
values present are nullified by it, therefore if more fine-grained access
control is desired, the ``all`` value should be removed from the LDAP entry
entirely. Client applications are free to implement the meaning  of the ``all``
value as they choose, however usually the usage in the LDAP search filter will
most likely be either ``all`` or some specific set of values.

Service permissions
~~~~~~~~~~~~~~~~~~~

The ``<service>`` value usually means a specific network service daemon, for
example ``sshd``, ``slapd``, ``vsftpd`` and so on. Since web applications are
accessed via a web server, they should use their own separate service or system
names to allow more fine-grained access control to each web application. The
value grants blanket access to a particular service without fine-grained
control over capabilities of the user.

System permissions
~~~~~~~~~~~~~~~~~~

The ``<system>`` value is an agnostic name for a set of various services that
work together as a whole to accomplish a task. For example, ``mail`` would
define an access control parameter for the SMTP server, IMAP server, mail
filtering software, and the ``shell`` string would define access control
parameter for the SSH service, :command:`sudo` access, NSS database service,
etc.

Similarly to the ``<service>`` value, this value grants blanket access to
a particular system as a whole. It means that the system cannot define "global"
access and "partial" access at the same time (see below). It might be hard to
convert a "global" access permissions to "partial" access permissions,
therefore the choice of how to define the access should be selected early on
during development.

Partial system permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``<system>:<type>`` value is a definition of a system access permissions
which are split into "parts" of the whole, each part defined by the permission
``<type>``. The partial permissions shouldn't overlap (two or more permissions
controlling the same resource access) or be additive (a permission type
implying presence of another permission type). There shouldn't be
a ``<system>:all`` permission as well, since it would nullify partial
permissions for a given system.

Each system can define its own set of permission types, however the type names
should be as precise and descriptive as possible. A good example is the "mail"
system, with the ``mail:receive`` permission allowing incoming messages to be
received by the e-mail account, the ``mail:send`` permission allowing outgoing
messages to be sent by the e-mail account, and the ``mail:access`` permission
granting read-write access to the e-mail account by its user.

It's easy to create additional permission types once the system is implemented,
therefore in larger systems this should be a preferred method of access
control. The partial permissions shouldn't be mixed with the "global"
permission for a given system because that would nullify the partial
permissions.

Examples of LDAP search queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get list of access control values of a given user account:

.. code-block:: console

   ldapsearch -Z -b 'uid=$username,ou=People,dc=example,dc=org' authorizedService

Find all personal accounts which have shell access or global access:

.. code-block:: console

   ldapsearch -Z -b "ou=People,dc=example,dc=org" \
              "(& (objectClass=inetOrgPerson) (| (authorizedService=all) (authorizedService=shell) ) )" dn

Find all LDAP entries which can send e-mail messages or have global access:

.. code-block:: console

   ldapsearch -Z -b "dc=example,dc=org" \
              "(| (authorizedService=all) (authorizedService=mail:send) )" dn


Host-based access control
-------------------------

The ``hostObject`` LDAP object class gives LDAP entries access to the ``host``
attribute which is used to store hostnames and Fully Qualified Domain Names of
the LDAP entries. The attribute type supports substring (wildcard) matches and
can be used to create host-based access rules.

Various services and systems can check for the presence of the ``host``
attribute with specific value patterns. The preferred value format in this case
should be: ``<service|system>:<host>``, where the ``<host>`` can be a FQDN
hostname, or a woldcard domain (``*.example.org``), or just a hostname, or the
value ``all`` for all hosts in the cluster.

Examples of LDAP search queries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Get list of POSIX accounts which should be present on a given host and have
access to shell services:

.. code-block:: console

   ldapsearch -Z -b "dc=example,dc=org" \
              "(& (objectClass=posixAccount) (| (host=shell:host.example.org) (host=shell:all) ) )"

Get list of POSIX accounts which should be present on any host in a specific
domain. This uses the substring match to get all entries with a specific
domain:

.. code-block:: console

   ldapsearch -Z -b "dc=example,dc=org" \
              "(& (objectClass=posixAccount) (| (host=shell:*.example.org) (host=shell:all) ) )"

Get list of POSIX accounts which should be present on all hosts in a specific
domain. This query looks for all entries with a wildcard (``*.example.org``)
domain defined as the value:

.. code-block:: console

   ldapsearch -Z -b "dc=example,dc=org" \
              "(& (objectClass=posixAccount) (| (host=shell:\2a.example.org) (host=shell:all) ) )"
