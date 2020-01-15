Default variable details
========================

Some of the ``debops.slapd`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.


.. _slapd__ref_tasks:

slapd__tasks
------------

The ``slapd__*_tasks`` variables define a custom set of ``ldap_entry`` and
``ldap_attrs`` Ansible module tasks that will be executed against the
:command:`slapd` ``cn=config`` configuration database, in the specified order.
These variables provide an easy and intuitive way to manage the OpenLDAP
configuration database, with some specific caveats due to how the ``cn=config``
configuration works. See the definition of the parameters for more details.

Examples
~~~~~~~~

Specify root credentials of the ``cn=config`` database. This entry ensures that
only the specific instance of the object attributes exists.

.. code-block:: yaml

   slapd__tasks:

     - name: 'Set cn=config root credentials'
       dn: [ 'olcDatabase={0}config', 'cn=config' ]
       attributes:
         olcRootDN: 'cn=admin,cn=config'
         olcRootPW: 'secret'
       state: 'exact'
       no_log: True

Ensure that specific object attributes in the main database are indexed by the
LDAP directory. This entry will add the specified indexes if they are not
configured, other existing sets of indexes will be left unchanged.

.. code-block:: yaml

   slapd__tasks:

     - name: 'Configure main database indexes'
       dn: [ 'olcDatabase={1}mdb', 'cn=config' ]
       attributes:
         olcDbIndex:
           - 'cn,uid eq'
           - 'member,memberUid eq'
           - 'objectClass eq'

Enable `Sync Provider overlay`__ for the main database. This entry creates a
new LDAP object if it doesn't exist, but it will not modify existing object or
its attributes.

.. __: http://www.zytrax.com/books/ldap/ch6/syncprov.html

.. code-block:: yaml

   slapd__tasks:

     - name: 'Enable sync provider overlay in main database'
       dn: 'olcOverlay={0}syncprov,olcDatabase={1}mdb,cn=config'
       objectClass: [ 'olcOverlayConfig', 'olcSyncProvConfig' ]
       attributes:
         olcOverlay: '{0}syncprov'

Define a basic Access Control List, based on the `example security policy`__.
This is an example of an object with `X-ORDERED`__ type attributes, which will
be added automatically by the ``ldap_attrs`` module included in DebOps.

.. __: http://www.zytrax.com/books/ldap/ch5/step2.html#step2
.. __: https://tools.ietf.org/html/draft-chu-ldap-xordered-00

.. code-block:: yaml

   slapd__tasks:

     - name: 'Set Access Control List in the main database'
       dn: 'olcDatabase={1}mdb,cn=config'
       attributes:
         olcAccess:

           - |-
             to attrs="userPassword"
             by self      write
             by anonymous auth
             by group.exact="cn=IT People,ou=Groups,dc=example,dc=com"
                          write
             by *         none

           - |-
             to attrs="carLicense,homePostalAddress,homePhone"
             by self       write
             by group.exact="cn=HR People,ou=Groups,dc=example,dc=com"
                           write
             by *          none

           - |-
             to *
             by self       write
             by group.exact="cn=HR People,ou=Groups,dc=example,dc=com"
                           write
             by users      read
             by *          none

       ordered: True
       state: 'exact'

Syntax
~~~~~~

The :envvar:`slapd__default_tasks`, :envvar:`slapd__tasks`,
:envvar:`slapd__group_tasks` and :envvar:`slapd__host_tasks` define a list of
YAML dictionaries, each list entry defines a ``ldap_entry`` or ``ldap_attrs``
task to perform on the local OpenLDAP ``cn=config`` database. The variables are
merged together in the order specified by the :envvar:`slapd__combined_tasks`
variable. The entries with the same ``name`` parameter will affect each other,
replacing the previously defined "instance" of a given task - this can be used
to change previously defined tasks conditionally.

The list of task parameters supported by the role:

``name``
  Required. The name of a given task, displayed during Ansible execution. It's
  an equivalent of the ``name`` keyword in Ansible tasks lists. Its value does
  not affect the actions performed in the ``cn=config`` database. Entries with
  the same name are merged together.

``dn``
  Required. The Distinguished Name of the LDAP directory object in the
  ``cn=config`` database which will be configured by a given entry. The value
  can be specified as a string or a YAML list, which will be joined by commas.

  This parameter is case-sensitive, if you use a wrong case here, the LDAP
  database will still most likely accept the configuration, but the task list
  will not be idempotent. When that happens, check the case of the DN value.

  This parameter can contain LDAP object names that use the ``X-ORDERED`` type
  syntax. The LDAP database will accept new objects that omit the ``X-ORDERED``
  syntax prefix, but subsequent executions of the role can cause errors due to
  incorrect DN name. It's best to specify the object prefix number directly
  from the start. Remember that the LDAP database can modify the ``X-ORDERED``
  prefix number on any modification of the list of objects; you should verify
  the current prefix numbering before applying any changes.

``objectClass``
  Optional. Specify a name or a YAML list of the LDAP Object Classes which
  should be used to define a new LDAP directory object.

  If this parameter is specified, the ``ldap_entry`` module will be used to
  perform the operation instead of ``ldap_attrs`` module. The ``ldap_entry``
  Ansible module will not modify the attributes of any existing LDAP directory
  objects, you need to use a separate configuration entry to do that, which
  does not specify this parameter.

  This parameter is case-sensitive, if you use a wrong case here, the LDAP
  database will still most likely accept the configuration, but the task list
  will not be idempotent. When that happens, check the case of the objectClass
  value(s). The parameter name is case-sensitive as well.

``attributes``
  Required. YAML dictionary which defines the attributes and their values of
  a given LDAP object. Each dictionary key is a case-sensitive name of an
  attribute, and the value is either a string, or a list of strings, or a list
  of YAML text blocks. If list is used for the values, multiple attribute
  entries will be created automatically.

  If you create configuration entries with the same ``name`` parameter, the
  ``attributes`` parameter will replace entirely the same parameter defined in
  previous entries on the list. This is not the case in the LDAP directory
  itself, where multiple separate configuration entries can define the same
  objects and their attributes multiple times, as long as the state is not
  specified or is set as ``present``. To ensure that a given set of attributes
  is specified only once in the LDAP database, you MUST define the ``state``
  parameter with the ``exact`` value.

  The attribute names are case-sensitive, if you use a wrong case here, the
  LDAP database will still most likely accept the configuration, but the task
  list will not be idempotent. When that happens, check the case of the
  attribute names.

  The attributes can contain lists that use the ``X-ORDERED`` type syntax. The
  LDAP database will accept new attribute values that omit the ``X-ORDERED``
  syntax prefix and a new prefix number will be assigned to them automatically
  by the LDAP directory. Subsequent executions of the role can create duplicate
  attribute values, if the prefix number is not specified. It's best to specify
  the attribute prefix number directly from the start. Remember that the LDAP
  database can modify the ``X-ORDERED`` prefix number on any modification of
  the list of attributes; you should verify the current prefix numbering before
  applying any changes.

``ordered``
  Optional, boolean. If defined and ``True``, the ``ldap_attrs`` Ansible module
  will automatically add the ``X-ORDERED`` index numbers to lists of values in
  all attributes of a current task. This extension is used in the OpenLDAP
  ``cn=config`` configuration database to define order of object attributes
  which are normally unordered.

  The most prominent use of the ``X-ORDERED`` extension is in the ``olcAccess``
  attribute, which defines the LDAP Access Control List. This attribute should
  be defined in a separate LDAP task, so that only its values will have the
  ``X-ORDERED`` index numbers inserted. Existing index values will be removed
  and replaced with the correct ordering defined by the YAML list.

``state``
  Optional. Possible values:

  ============ ================================================================
    State        Description
  ------------ ----------------------------------------------------------------
  ``present``  Default. The role will ensure that a given configuration entry
               is present in the LDAP directory.  There might be more more than
               one copy of a given entry present at the same time. To avoid
               creating duplicate entries, use ``exact`` instead of
               ``present``.
  ------------ ----------------------------------------------------------------
  ``exact``    The role will ensure that only the specified set of attributes
               of a given LDAP object is defined in the LDAP database. You MUST
               use this parameter when ``X-ORDERED`` type attributes are
               configured, otherwise the role cannot guarantee that only the
               specified set of attribute values, as well as their specified
               order, is defined in a given LDAP object.
  ------------ ----------------------------------------------------------------
  ``absent``   The specified attributes of a given LDAP object will be removed.
  ------------ ----------------------------------------------------------------
  ``init``     The role will prepare a task entry configuration but it will not
               be active - this can be used to activate prepared entries
               conditionally.
  ------------ ----------------------------------------------------------------
  ``ignore``   A given configuration entry will not be evaluated by the role.
               This can be used to conditionally enable or disable entries.
  ============ ================================================================

``entry_state``
  Optional. This parameter should be present only if the entire LDAP object
  entry is to be removed. Set the entry state to ``absent`` to remove it.

``no_log``
  Optional, boolean. If ``True``, a given task output will not be recorded to
  avoid emitting sensitive information like passwords. If not specified or
  ``False``, the task will be recorded and logged.

``run_once``
  Optional, boolean. If defined and ``True``, a given LDAP task will be
  executed only one time when the role is applied on multiple remote hosts at
  once. This might be important in cases where the LDAP directory is
  replicated, or values from different remote hosts can result in the same LDAP
  objects, e.g. objects with ``X-ORDERED`` index numbers, like LDAP schemas.


.. _slapd__ref_slapacl_tests:

slapd__slapacl_tests
--------------------

The ``slapd__slapacl_*_tests`` variables define a set of :man:`slapacl(8)`
tests to perform against the OpenLDAP ACL configuration. The tests are
generated and stored in a shell script which is then executed against the local
:command:`slapd` instance.

See :ref:`slapd__ref_acl` for more details about the default set of OpenLDAP
Access Control Lists defined by the :ref:`debops.slapd` role. The
:ref:`slapd__ref_acl_tests` section has more details about the ACL test
infrastructure built into the :ref:`debops.slapd` role.

Examples
~~~~~~~~

Check the access rules of a given LDAP object. Non-existent objects don't
generate an error. Existing objects will generate a list of ACL permissions.
To see the rules, pipe the script output to a different command or to a file.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Check access to ou=People,{{ slapd__basedn }}'
       dn: 'ou=People,{{ slapd__basedn }}'

Check the access rules of a given LDAP object by another LDAP object. To see
the rules, pipe the script output to a different command or to a file.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Check access to ou=People,{{ slapd__basedn }} by user'
       dn: 'ou=People,{{ slapd__basedn }}'
       authdn: 'uid=user,ou=People,{{ slapd__basedn }}'

Check the access rules of a given LDAP object by a SASL identity. To see the
rules, pipe the script output to a different command or to a file.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Check access to ou=People,{{ slapd__basedn }} by SASL user'
       dn: 'ou=People,{{ slapd__basedn }}'
       uid: 'user'

Test the access policy of a specific LDAP object, accessed by anonymous user.
Failed policy test will result in an error.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Test access to ou=People,{{ slapd__basedn }} by anonymous user'
       dn: 'ou=People,{{ slapd__basedn }}'
       authdn: ''
       policy: 'none(=0)'

Test the access policy of a specific LDAP object attribute, accessed by another
LDAP entry. Failed policy test will result in an error.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Test write access to ou=People,{{ slapd__basedn }} by a service'
       dn: 'ou=People,{{ slapd__basedn }}'
       authdn: 'uid=service,ou=Services,{{ slapd__basedn }}'
       query: 'entry/write'
       policy: 'deny'

Test the access policy of a specific LDAP object attribute, accessed on behalf
of a LDAP user by a LDAP service entry via SASL proxy authorization. Failed
policy test will result in an error.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Test write access to ou=People,{{ slapd__basedn }} by another user'
       dn: 'ou=People,{{ slapd__basedn }}'
       authdn: 'uid=service,ou=Services,{{ slapd__basedn }}'
       authzid: 'dn:uid=user,ou=People,{{ slapd__basedn }}'
       query: 'entry/write'
       policy: 'allow'

Test the access rules of a LDAP object, accessed by another LDAP entry. Failed
rule test will result in an error.

.. code-block:: yaml

   slapd__slapacl_tests:

     - name: 'Test access rules for ou=People,{{ slapd__basedn }} by user'
       dn: 'ou=People,{{ slapd__basedn }}'
       authdn: 'uid=user,ou=People,{{ slapd__basedn }}'
       queries:

         - name: 'description/write'
           result: 'write access to description: ALLOWED'

         - name: 'entry'
           result: 'entry: manage(=mwrscxd)'

Syntax
~~~~~~

The ACL tests are defined using a list of YAML dictionaries. Each dictionary
describes one test using specific parameters:

``name``
  Required. The descriptive name of the test, not used otherwise. Each test has
  to have an unique ``name`` parameter. The configuration entries with the same
  ``name`` are merged together and can affect each other in order of
  appearance.

``dn``
  Required. The Distinguished Name of the LDAP object to test.

``authdn``
  Optional. The Distinguished Name of the LDAP object which is used as the
  identity which accesses the tested object.

``uid``
  Optional. The SASL id (login name) which will be mapped to a LDAP object
  using the configured ``authz-regexp`` rules configured in the OpenLDAP
  server. This LDAP object will be used as the identity which accesses the
  tested object.

``authzid``
  Optional. The `SASL proxy authorization`__ id (login name) prefixed with
  ``u:``, which will be mapped to a LDAP object using the ``authz-regexp``
  rules configured in the OpenLDAP server, or Distinguished Name of an LDAP
  object prefixed with ``dn:``. The ``authdn`` or ``uid`` LDAP object will use
  the ``authzid`` object to access the test subject.

  .. __: https://www.openldap.org/doc/admin24/sasl.html#SASL%20Proxy%20Authorization

``options``
  Optional. List of addiontal :man:`slapacl(8)` option which should be used for
  a particular test, for example:

  .. code-block:: yaml

     options: [ 'ssf="128"' ]

  The option values are not quoted in the script template and need to be quoted
  in the parameter if necessary.

``dry_run``
  Optional, boolean. If ``True``, instead of using a real ``dn`` LDAP object
  from the directory, the :command:`slapacl` command will generate a fake DN
  entry with no attributes which can be used to simulate non-existent LDAP
  objects. This is required by certain backend databases, for example
  ``cn=config``.

  ACL rules tested against the attributes of the fake DN entry might not be
  accurate, use this only with tests against entries themselves.

``debug``
  Optional. Enable debugging and set the desired log level as a string.
  Supported log levels can be seen by running the :command:`slapd -d ?`
  command, or can be found in the :man:`slapd-config(5)` manual page in the
  ``olcLogLevel`` option documentation. In the case of the ACL tests, the
  useful log level can be ``acl``.

``state``
  Optional. If not specified or ``present``, a given test will be included in
  the generated script. If ``absent``, the test will not be included in the
  script. If ``ignore``, a given configuration entry will not be evaluated by
  the role.

  If ``init``, a given configuration entry will be prepared, but not actually
  included in the generated script. Such entries can then be enabled
  conditionally by another entry with the same ``name`` parameter.

``comment``
  Optional. String or YAML text block with comments about a given tests. The
  comments will be included in the actual script and not displayed otherwise.

``query``
  Optional. Specify the attribute, optionally an access level and a value to
  which a given ``dn`` LDAP object should have access, for example ``cn/write``
  or ``o/write:Example Org``. You can also specify ``entry``, to test access to
  a given LDAP object without specific attributes (this is the default if
  ``query`` parameter is not specified) or ``children`` to specify access to
  child objects of a given LDAP object.

``policy``
  Optional. Specify the access policy of a given ACL test. If a given test
  checks particular attribute with a specific access level, for example
  ``cn/write``, you can define the policy using keywords ``allow``,
  ``allowed``, ``accept``, ``grant``, ``permit`` to allow access, or
  ``disallow``, ``denied``, ``reject``, ``revoke``, ``deny`` to deny access to
  a given attribute.

  If the test checks access policy for an ``entry``, ``children``, or if
  a ``query`` parameter is not specified, the ``policy`` parameter needs to
  have an exact permission set for the script to successfully compare the
  :command:`slapacl` command output with the desired policy. For example, the
  ``read`` access needs to be specified as ``read(=rscxd)``. Check the script
  output to see the expected value if you are unsure what needs to be set as
  the ``policy`` value.

``queries``
  Optional. A list of YAML dictionaries, each dictionary defines an attribute
  test similar to the ``query``/``policy`` combination. This parameter can be
  used to define more complex ACL rule test cases where different object
  attributes have different access policies. Tests defined using the
  ``queries`` parameter use the :command:`diff` command to compare the results.

  The ``queries`` parameters from tests with the same ``name`` parameters are
  merged together, and their entries can modify each other when they have the
  same ``name`` value.

  Each test case is defined using specific paramters:

  ``name``
    Required. The attribute to test, with optional access level and value,
    similar to the ``query`` parameter, for example ``ou/write``.

  ``result``
    Optional. Specify the exact line that contains the result of a given test
    case. You can inspect the output of the test script to find what needs to
    be defined here.

  ``state``
    Optional. If not defined or ``present``, a given test case will be included
    in the test script. If ``absent``, a given test case will not be included
    in the test script.
