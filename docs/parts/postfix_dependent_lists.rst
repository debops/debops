postfix_dependent_lists
~~~~~~~~~~~~~~~~~~~~~~~

This variable can be used in Postfix dependency role definition to configure
additional lists used in Postfix main.cf configuration file. This variable
will be saved in Ansible facts and updated when necessary.

Examples
''''''''

Append custom tables to ``transport_maps`` option::

    transport_maps: [ 'hash:/etc/postfix/transport' ]

Append a given list of alias maps if Postfix has ``local`` capability::

    alias_maps:
      - capability: 'local'
        list: [ 'hash:/etc/aliases' ]

Append this virtual alias map if Postfix does not have ``local`` capability::

    virtual_alias_maps:
      - no_capability: 'local'
        list: [ 'hash:/etc/postfix/virtual_alias_maps' ]

