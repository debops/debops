Default variable details
========================

Some of the ``debops.ldap`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.


.. _ldap__ref_configuration:

ldap__configuration
-------------------

The ``ldap__*_configuration`` variables define the contents of the
:file:`/etc/ldap/ldap.conf` configuration file. The variables are merged in
order defined by the :envvar:`ldap__combined_configuration` variable, which
allows modification of the default configuration through the Ansible inventory.
See :man:`ldap.conf(5)` for possible configuration parameters and their values.

Examples
~~~~~~~~

See :envvar:`ldap__default_configuration` variable for an example of existing
configuration.

Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
specific parameters:

``name``
  Required. Name of the :man:`ldap.conf(5)` configuration option. The
  configuration options with the same ``name`` parameter will be merged in
  order of appearance.

  In the generated configuration file, the option name will be automatically
  converted to uppercase.

``value``
  Required. The value of a given configuration option. It can be either
  a string, a YAML list (elements will be joined with spaces).

``state``
  Optional. If not defined or ``present``, a given configuration option will be
  included in the generated configuration file. If ``absent``, a given
  configuration option will be removed from the generated file. If ``comment``,
  the option will be included, but commented out and inactive. If ``ignore``,
  the role will not evaluate the configuration entry during template
  generation, this can be used for conditional activation of
  :man:`ldap.conf(5)` configuration options.

``comment``
  Optional. String or YAML text block that contains comments about a given
  configuration option.

``separator``
  Optional, boolean. If ``True``, and additional empty line will be added
  before a given configuration option to separate it from the other options for
  readability.


.. _ldap__ref_tasks:

ldap__tasks
-----------

The ``ldap__*_tasks`` variables define a custom set of ``ldap_entry`` and
``ldap_attrs`` Ansible module tasks that will be executed against the
LDAP directory, in the specified order. This also requires that the role can
access the LDAP credentials of the Ansible user, on the Ansible Controller. See
the :ref:`ldap__ref_admin` for more details; this section describes the syntax
of the LDAP tasks themselves.

.. note:: Remember, these are not "Ansible tasks", they are "LDAP tasks"
          performed in the LDAP directory itself, via Ansible Controller.

Examples
~~~~~~~~

See the :envvar:`ldap__default_tasks` for an example of the default LDAP tasks
used by the role.

Create the ``ou=People`` branch of the LDAP directory, add a new user account,
and set its password, and some other attributes. This example assumes that LDAP
directory will hash the provided password after checking its quality. The
``ldap__*`` variables are defined as the :ref:`debops.ldap` default variables,
but can be overridden via the inventory.

.. code-block:: yaml

   ldap__tasks:

     - name: 'Create the ou=People object'
       dn: '{{ [ ldap__people_rdn ] + ldap__base_dn }}'
       objectClass: [ 'organizationalUnit' ]
       attributes:
         ou: '{{ ldap__people_rdn.split("=")[1] }}'

     - name: 'Create the uid={{ ansible_user }} object'
       dn: '{{ [ 'uid=' + ansible_user, ldap__people_rdn ] + ldap__base_dn }}'
       objectClass: [ 'inetOrgPerson' ]
       attributes:
         cn: 'Ansible User'
         sn: 'User'
         uid: '{{ ansible_user }}'
         userPassword: 'secret'

Remove the default ``cn=admin,dc=example,dc=org`` LDAP object created in the
directory by the Debian ``slapd`` APT package. It's not needed after an admin
account has been created.

.. code-block:: yaml

   ldap__tasks:

     - name: 'Remove the default admin account'
       dn: 'cn=admin,{{ ldap__basedn }}'
       state: 'absent'
       entry_state: 'absent'

Syntax
~~~~~~

The :envvar:`ldap__default_tasks`, :envvar:`ldap__tasks`,
:envvar:`ldap__group_tasks` and :envvar:`slapd__host_tasks` define a list of
YAML dictionaries, each list entry defines a ``ldap_entry`` or ``ldap_attrs``
task to perform in the LDAP directory. The variables are
merged together in the order specified by the :envvar:`ldap__combined_tasks`
variable.

When the :ref:`debops.ldap` role is used as a dependency, only the
:envvar:`ldap__dependent_tasks` variable will be included in the
:envvar:`ldap__combined_tasks` list, the default tasks or the ones specified in
the Ansible inventory will not be evaluated. See :ref:`ldap__ref_dependency`
for more details.

The entries with the same ``name`` parameter will affect each other, replacing
the previously defined "instance" of a given task - this can be used to change
previously defined tasks conditionally.

The list of task parameters supported by the role:

``name``
  Required. The name of a given task, displayed during Ansible execution. It's
  an equivalent of the ``name`` keyword in Ansible tasks lists. Its value does
  not affect the actions performed in the LDAP directory. Entries with the same
  name are merged together.

``dn``
  Required. The Distinguished Name of the LDAP directory object which will be
  configured by a given entry. The value can be specified as a string or a YAML
  list, which will be joined by commas.

  This parameter is case-sensitive, if you use a wrong case here, the LDAP
  directory will still most likely accept the configuration, but the task list
  will not be idempotent. When that happens, check the case of the DN value.

  This parameter can contain LDAP object names that use the ``X-ORDERED`` type
  syntax. The LDAP directory will accept new objects that omit the
  ``X-ORDERED`` syntax prefix, but subsequent executions of the role can cause
  errors due to incorrect DN name. It's best to specify the object prefix
  number directly from the start. Remember that the LDAP directory can modify
  the ``X-ORDERED`` prefix number on any modification of the list of objects;
  you should verify the current prefix numbering before applying any changes.

``objectClass``
  Optional. Specify a name or a YAML list of the LDAP Object Classes which
  should be used to define a new LDAP directory object.

  If this parameter is specified, the ``ldap_entry`` module will be used to
  perform the operation instead of ``ldap_attrs`` module. The ``ldap_entry``
  Ansible module will not modify the attributes of any existing LDAP directory
  objects, you need to use a separate configuration entry to do that, which
  does not specify this parameter.

  This parameter is case-sensitive, if you use a wrong case here, the LDAP
  directory will still most likely accept the configuration, but the task list
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
  is specified only once in the LDAP directory, you MUST define the ``state``
  parameter with the ``exact`` value.

  The attribute names are case-sensitive, if you use a wrong case here, the
  LDAP directory will still most likely accept the configuration, but the task
  list will not be idempotent. When that happens, check the case of the
  attribute names.

  The attributes can contain lists that use the ``X-ORDERED`` type syntax. The
  LDAP directory will accept new attribute values that omit the ``X-ORDERED``
  syntax prefix and a new prefix number will be assigned to them automatically
  by the LDAP directory. Subsequent executions of the role can create duplicate
  attribute values, if the prefix number is not specified. It's best to specify
  the attribute prefix number directly from the start. Remember that the LDAP
  directory can modify the ``X-ORDERED`` prefix number on any modification of
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
               of a given LDAP object is defined in the LDAP directory. You
               MUST use this parameter when ``X-ORDERED`` type attributes are
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
