postfix_dependent_maincf
~~~~~~~~~~~~~~~~~~~~~~~~

Here you can specify Postfix configuration options which should be enabled in
``/etc/postfix/main.cf`` using debops.postfix dependency role definition.
Configuration will be saved in Ansible facts and updated when necessary.

Examples
''''''''

Add this option in ``main.cf``::

    postfix_dependent_maincf:
      - param: 'local_destination_recipient_limit'
        value: '1'

Enable this option only if ``mx`` is in Postfix capabilities::

    postfix_dependent_maincf:
      - param: 'defer_transports'
        value: 'smtp'
        capability: 'mx'

Enable this option only if ``local`` is not in Postfix capabilities::

    postfix_dependent_maincf:
      - param: 'relayhost'
        value: 'mx.example.org'
        no_capability: 'local'

If no value is specified, check if a list of the same name as param exists
in ``postfix_dependent_lists`` and enable it::

    postfix_dependent_maincf:
      - param: 'virtual_alias_maps'

