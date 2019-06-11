Default variable details
========================

Some of the ``debops.pam_access`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.


.. _pam_access__ref_rules:

pam_access__rules
-----------------

The ``pam_access__*_rules`` variables define the state of the
:file:`/etc/security/access*.conf` configuration files and their contents.
The variables are merged in order defined by the
:envvar:`pam_access__combined_rules` variable, which allows modification of the
default configuration through the Ansible inventory.

Examples
~~~~~~~~

Include some of the examples from the :man:`access.conf(5)` manual page in the
global :file:`/etc/security/access.conf` configuration file. Note that the
configuration is explicitly enabled because the role does not configure the
global access list by default:

.. code-block:: yaml

   pam_access__rules:

     - name: 'global'
       state: 'present'
       options:

         - name: 'allow-root-locally'
           comment: |
             User root should be allowed to get access via cron, X11 terminal :0, tty1-6
           permission: 'allow'
           users: 'root'
           origins: [ 'crond', ':0', 'tty1', 'tty2', 'tty3', 'tty4', 'tty5', 'tty6' ]

         - name: 'allow-root-loopback'
           permission: '+'
           users: 'root'
           origins: '127.0.0.1'

         - name: 'allow-root-subnet'
           comment: |
             User root should get access from network 192.0.2. which can also be
             specified using a CIDR prefix, 192.0.2.0/24
           permission: 'allow'
           users: 'root'
           origins: [ '192.0.2.', '192.0.2.0/24' ]

         - name: 'allow-root-domain'
           comment: |
             User root should be able to have access from a specific domain
           permission: '+'
           users: 'root'
           origins: '.example.org'

         - name: 'deny-root'
           comment: |
             Deny access to the root account from any other sources
           permission: 'deny'
           users: 'root'
           origins: 'ALL'

         - name: 'allow-foo-admins'
           comment: |
             User 'foo' and members of netgroup 'admins' should be allowed to get
             access from all sources. This will only work if netgroup service is
             available.
           permission: '+'
           users: [ '@admins', 'foo' ]
           origins: 'ALL'

         - name: 'allow-john-ipv6subnet'
           comment: |
             User 'john' should get access from IPv6 net/mask.
           permission: 'allow'
           users: 'john'
           origins: '2001:db8:0:101::/64'

         - name: 'allow-local-wheel'
           comment: |
             Disallow console logins to all but the 'shutdown', 'sync' and all
             other accounts, which are a member of the 'wheel' group.
           permission: '-'
           groups_except: 'wheel'
           users_except: [ 'shutdown', 'sync' ]
           origins: 'LOCAL'

         - name: 'deny-all'
           comment: |
             All other users should be denied access from all sources. This rule
             will be placed at the end of the configuration, to allow easy
             addition of more rules before it.
           permission: 'deny'
           users: 'ALL'
           origins: 'ALL'
           weight: 99999

Add some of the examples from the default :file:`/etc/security/access.conf`
file installed by Debian to the :file:`/etc/security/access-sshd.conf`
configuration file used by the ``sshd`` service.

Note that the configuration has state ``append`` which means that even though
the values are defined in the Ansible inventory, they will only be applied when
the :ref:`debops.pam_access` role is used in the context of the
:ref:`debops.sshd` role, via the ``sshd.yml`` playbook (the configuration entry
was defined elsewhere and inventory entry is appended to it). Otherwise the
custom access file used by the ``sshd`` service would be overwritten during
normal usage of the :ref:`debops.pam_access` role.

The examples are nonsensical in the context of the OpenSSH service, but are
provided here to show how to implement specific ACL rules.

.. code-block:: yaml

   pam_access__rules:

     - name: 'sshd'
       state: 'append'
       options:

         - name: 'deny-non-root'
           comment: 'Disallow non-root logins on tty1'
           permission: 'deny'
           users_except: 'root'
           origins: 'tty1'

         - name: 'deny-non-privileged'
           comment: 'Disallow non-local logins to privileged accounts'
           permission: '-'
           groups: 'wheel'
           origins_except: [ 'LOCAL', '.sub.example.org' ]

Syntax
~~~~~~

The variables contain a list of YAML dictionaries, each dictionary can have
specific parameters:

``name``
  Required. Name of an access control configuration file managed by the
  :ref:`debops.pam_access` role. The role will create the file in:

  .. code-block:: none

     /etc/security/access-<name>.conf

  Configuration entries with the same ``name`` parameter will be merged
  together in order of appearance; this can be used to modify existing entries
  via the Ansible inventory.

``filename``
  Optional. Override the autogenerated file name. You should only specify the
  filename itself, files are stored in the :file:`/etc/security/` directory.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  generated. If ``absent``, the specified configuration file will be removed.
  If ``init``, the configuration entry will be initialized, but not active
  - this can be used to prepare an entry and activate it conditionally later.
  If ``ignore``, a given configuration entry will not be evaluated by the role.

  If ``append``, the configuration entry will be processed only if a given
  entry was defined earlier. This should be a preferred method to modify access
  rules defined by other Ansible roles through the Ansible inventory, otherwise
  the user roles will override the role rules.

``divert``
  Optional, boolean. If ``True``, the role will automatically divert or revert
  the original access control rule file depending on its state, to preserve it
  for APT upgrades. This parameter shouldn't be changed if a diverted file is
  present, otherwise the role will not track the diversion.

``fieldsep``
  Optional. Specify the character that will be used as the field separator in
  the generated rule files. If not specified, colon (``:``) is used by default.
  See :man:`pam_access(8)` for information about the usage of this parameter.

``listsep``
  Optional. Specify the character that will be used as the list element
  separator in the generated rule files. If not specified, space is used by
  default. See :man:`pam_access(8)` for information about the usage of this
  parameter.

``options``
  Required. List of YAML dictionaries which describe PAM access rules. The
  lists in the entries with the same ``name`` parameter are merged together,
  with the rules that use the same ``name`` affecting each other in order of
  appearance. Rules can be defined using specific parameters:

  ``name``
    Required. Name of a given access rule, not used directly. Entries with the
    same ``name`` parameter will be merged together in order of appearance;
    this allows modification of existing entries via Ansible inventory.

  ``permission``
    Required. Specify the permission of a given access rule. Possible values:

    - ``allow`` / ``+`` / ``accept``
    - ``deny`` / ``-`` / ``decline``

  ``users``
    String or YAML list of usernames, netgroups or ``ALL`` that matches
    everyone. If ``users_except`` parameter is specified, this parameter is
    ignored.

  ``users_except``
    String or YAML list of usernames, netgroups or ``ALL`` that matches
    everyone. If this parameter is specified, the list of users or groups will
    be prefixed with ``ALL EXCEPT`` which allows for negation.

  ``groups``
    String or YAML list of UNIX group names, which will be automatically
    wrapped in parentheses (``( )``) to mark them as groups. If
    ``groups_except`` parameter is specified, this parameter is ignored.

  ``groups_except``
    String or YAML list of UNIX group names, which will be automatically
    wrapped in parentheses (``( )``) to mark them as groups. If this parameter
    is specified, the list of users or groups will be prefixed with ``ALL
    EXCEPT`` which allows for negation.

  ``origins``
    String or YAML list of "origins" - TTY names, hostnames, domain names
    (specified with the ``.`` prefix), IP addresses, network addresses
    (specified with the ``.`` suffix or with CIDR netmask), netgroup names,
    ``ALL`` which matches everything, or ``LOCAL`` which matches only local
    TTYs and services. If ``origins_except`` parameter is specified, this
    parameter is ignored.

  ``origins_except``
    String or YAML list of "origins" - TTY names, hostnames, domain names
    (specified with the ``.`` prefix), IP addresses, network addresses
    (specified with the ``.`` suffix or with CIDR netmask), netgroup names,
    ``ALL`` which matches everything, or ``LOCAL`` which matches only local
    TTYs and services. If this parameter is specified, the list of origins will
    be prefixed with ``ALL EXCEPT`` which allows for negation.

  ``comment``
    Optional. String or YAML text block that contains comments about a given
    access rule.

  ``state``
    Optional. If not specified or ``present``, a given access rule will be
    included in the generated rule file. If ``absent``, the rule will be
    removed from the generated rule file.

  ``weight``
    Optional. Positive or negative number, which can be used to affect the
    position of the rule within the rule file. Positive numbers will force the
    rule to be lower than normal (adding weight), negative numbers will move
    the role higher on the list (substracting weight).
