.. _postfix__ref_defaults_detailed:

Default variable details
========================

some of ``debops.postfix`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


postfix__maincf
---------------

Configuration of the ``postfix__*_maincf`` variables is described in a separate
document, :ref:`postfix__ref_maincf`.


postfix__mastercf
-----------------

Configuration of the ``postfix__*_mastercf`` variables is described in
a separate document, :ref:`postfix__ref_mastercf`.


.. _postfix__ref_maincf_sections:

postfix__maincf_sections
------------------------

The :file:`/etc/postfix/main.cf` configuration file is managed using informal
"sections", each section groups the common Postfix options.

The :envvar:`postfix__maincf_sections` variable contains a list of sections defined
by YAML dictionaries with specific parameters:

``name``
  Required. Short name of the section, used in the configuration
  parameters to put a given option in a particular section.

``title``
  Optional. A short description of the section included as its header.

``state``
  Optional. If not specified or ``present``, the section will be added in the
  configuration file. If ``absent``, the section will not be included in the
  file.

Examples
~~~~~~~~

Define a set of configuration sections:

.. code-block:: yaml

   postfix__maincf_sections:

     - name: 'base'

     - name: 'admin'
       title: 'Administrator options'

     - name: 'unknown'
       title: 'Other options'


.. _postfix__ref_lookup_tables:

postfix__lookup_tables
----------------------

The ``postfix__*_lookup_tables`` variables can be used to manage
`Postfix lookup tables <http://www.postfix.org/DATABASE_README.html>`_.
Each lookup table is a separate file located in the :file:`/etc/postfix/`
directory. The entries in the variables are merged together, therefore by using
the same ``name`` key in multiple entries you can modify existing
configuration, for example through Ansible inventory.

The lookup tables can be defined by other roles via role dependent variables,
however the state of each dependent role is not tracked. Because of that it's
best to use separate lookup tables for each Ansible role and join them together
at the Postfix configuration level, via options defined in the :file:`main.cf`
or :file:`master.cf` configuration files.

Each entry that manages a lookup table is a YAML dictionary with specific
parameters:

``name``
  Required. Name of the lookup table to manage, it will be a file in the
  :file:`/etc/postfix/` directory. This parameter is used as an anchor to merge
  separate entries together.

  Files which names end with the ``*.in`` extension are assumed to be hashed
  tables, and will be processed automatically by :command:`make` when any
  changes are detected during role execution.

``state``
  Optional. If not specified or ``present``, the lookup table will be
  generated. If ``absent``, the lookup table will be removed (hashed table
  files are not removed automatically). If ``ignore``, a given configuration
  entry will not be evaluated by Ansible.

``owner``
  Optional. The UNIX account which will be the owner of the generated file. If
  not specified, ``root`` will be used by default.

``group``
  Optional. The UNIX group which will be the primary group of the generated
  file. If not specified, ``postfix`` will be used by default.

``mode``
  Optional. The attributes set on the generated file. If not specified,
  ``0640`` will be set by default.

  If you specify ``0600`` or ``0640`` file attributes, the task which manages
  the file will automatically set the ``no_log`` Ansible parameter to ``True``,
  so that the contents of the file are not logged or displayed during Ansible
  execution.

``no_log``
  Optional, boolean. If not specified or ``False``, the task will be processed
  normally. If ``True``, the task execution will not be logged and any file
  contents will not be displayed in the Ansible output.

The parameters below are related to the contents of the lookup table file:

``comment``
  Optional. String or YAML text block with a comment added at the beginning of
  the lookup table file.

``raw``
  Optional. String or YAML text block with the file contents which will be
  stored "as-is" in the lookup table file.

``config``
  Optional. An YAML dictionary which defines an external Postfix lookup table,
  for example in a SQL database. Each dictionary key is an option name, and
  dictionary value is the option value. Values can be either strings or YAML
  lists. See the manpage of specific lookup tables for the supported options.

``connection``
  Optional. An YAML dictionary which uses the same syntax as the ``config``
  parameter. The ``connection`` parameter can be used to define connection
  details for a particular database in a separate YAML dictionary, which then
  can be referenced in multiple lookup tables at once with different query
  configuration. See the examples below for an example usage.

``options``
  Optional. An YAML list with lookup table entries. Each entry is a YAML
  dictionary. If the dictionary has a ``name`` key, it will be interpreted as
  an extended entry with specific parameters:

  ``name``
    The lookup key used by Postfix to find the specific entry in the table.

  ``value``
    The value or action returned by the lookup table.

  ``state``
    Optional. If not specified or ``present``, a given lookup table entry will
    be added in the file. If ``absent``, a given entry will be removed from the
    file. If ``ignore``, a given configuration will not be parsed by Ansible.
    If ``comment``, a given lookup table entry will be added but commented out.

  ``comment``
    Optional. A string or YAML text block with a comment related to a given
    lookup table entry.

  If the ``name`` parameter is not found, first entry in a YAML dictionary is
  parsed as a key/value lookup table entry.

  When a given lookup table is defined by multiple entries, the ``options``
  parameters are merged together.

``content``
  Optional. An YAML list with lookup table entries. Each entry can be a string
  that defines a lookup table key, its value will be defined by the
  ``default_action`` parameter. Otherwise you can specify parameters similar to
  those supported by the ``options`` list. Contents of the ``content``
  parameter are appended to the ``options`` contents. The ``content``
  parameters from multiple entries are not merged together.

``default_action``
  Optional. The default action defined for the lookup table entries that don't
  specify one themselves.

If the ``connection`` or ``config`` parameters are specified, for convenience
you can specify the options that control the lookup table configuration from
the :man:`ldap_table(5)`, :man:`mysql_table(5)`, :man:`sqlite_table(5)` and
:man:`pgsql_table(5)` as the lookup table parameters, on the same level as the
``name`` parameter.

Examples
~~~~~~~~

.. _postfix__ref_lookup_tables_example_alias_maps:

Define a set of virtual mail aliases using a raw YAML text block, stored in
a hashed lookup table:

.. code-block:: yaml

   postfix__lookup_tables:

     - name: 'virtual_alias_maps.in'
       raw: |
         name.surname@example.org     user1@example.org
         name.othername@example.org   user2@example.org

   postfix__maincf:
     - virtual_alias_maps: [ 'hash:${config_directory}/virtual_alias_maps' ]


.. _postfix__ref_lookup_tables_example_mailbox_maps:

Define virtual mailbox table stored in a MySQL database. Lookup table file will
be only readable by the ``root`` account to secure the password for the
database:

.. code-block:: yaml

   postfix__lookup_tables:

     - name: 'virtual_mailbox_maps.cf'
       config:
         hosts:    [ 'db1.example.net', 'db2.example.net' ]
         user:     'mailuser'
         password: 'mailpassword'
         dbname:   'mail'
         query:    "SELECT maildir FROM mailbox WHERE local_part='%u' AND domain='%d' AND active='1'"

   postfix__maincf:
     - virtual_mailbox_maps: [ 'proxy:mysql:${config_directory}/virtual_mailbox_maps.cf' ]

The same example with connection details defined in a separate variable which
can be reused in multiple lookup tables:

.. code-block:: yaml

   db_connection:
     hosts:    [ 'db1.example.net', 'db2.example.net' ]
     user:     'mailuser'
     password: 'mailpassword'
     dbname:   'mail'

   postfix__lookup_tables:

     - name: 'virtual_mailbox_maps.cf'
       connection: '{{ db_connection }}'
       query:      "SELECT maildir FROM mailbox WHERE local_part='%u' AND domain='%d' AND active='1'"

   postfix__maincf:
     - virtual_mailbox_maps: [ 'proxy:mysql:${config_directory}/virtual_mailbox_maps.cf' ]

Note that the parameters of a particular table can be defined on the same level
as the ``name`` parameter, for ease of use.


.. _postfix__ref_lookup_tables_example_banned_helo:

Create a list of banned HELO/EHLO names which contains the host's IP addresses
and FQDN hostname, stored in a hashed lookup table:

.. code-block:: yaml

   postfix__lookup_tables:

     - name: 'banned_helo_names.in'
       content: '{{ ansible_all_ipv4_addresses + ansible_all_ipv6_addresses
                    + [ ansible_fqdn, "localhost", "127.0.0.1" ] }}'
       default_action: 'REJECT You are not me'

   postfix__maincf:

     - name: 'smtpd_helo_restrictions'
       value:
         - name: 'check_helo_access hash:${config_directory}/banned_helo_names'
           weight: -100


.. _postfix__ref_lookup_tables_example_client_access:

Create a CIDR lookup table that contains a custom blacklist/whitelist of
networks that can talk to the SMTP 'submission' service:

.. code-block:: yaml

   postfix__lookup_tables:

     - name: 'submission_client_access.cidr'
       options:

         - name: '192.0.2.0/24'
           value: 'REJECT Connections not allowed from TEST-NET-1 network'

         - '10.10.0.0/16': 'OK'

   postfix__maincf:

     - name: 'submission_smtpd_client_restrictions'
       value:
         - 'check_client_access cidr:${config_directory}/submission_client_access.cidr'
         - 'reject'

   postfix__mastercf:

     - name: 'submission'
       options:
         - name: 'smtpd_client_restrictions'
           value: '${submission_smtpd_client_restrictions}'
