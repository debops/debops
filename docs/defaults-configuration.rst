Default variables: configuration
================================

some of ``debops.postfix`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _postfix_capabilities:

postfix_capabilities
--------------------

List of active Postfix capabilities. By default Postfix is configured with
local mail disabled, all mail is sent to a local MX server configured in DNS.

List of available Postfix capabilities:

``null``
  **Enabled by default.** Postfix has no local delivery, all mail is sent to a
  MX for the current domain. These settings are based on `Postfix null client`_
  configuration.

  You should remove this capability and replace it with others presented below.

  .. _Postfix null client: http://www.postfix.org/STANDARD_CONFIGURATION_README.html#null_client

``local``
  local delivery is enabled on current host.

``network``
  enables access to Postfix-related ports (``25``, ``587``, ``465``)
  in the firewall which is required for incoming mail to be accepted by
  Postfix.

``mx``
  enables support for incoming mail on port ``25``, designed for hosts set up
  as MX. Automatically enables ``postscreen`` (without ``dnsbl``/``dnswl`` support),
  anti-spam restrictions.

``submission``
  enables authorized mail submission on ports ``25`` and ``587``
  (user authentication is currently not supported and needs to be
  configured separately).

``deprecated``
  designed to enable obsolete functions of the mail system,
  currently enables authorized mail submission on port ``465`` (when
  ``submission`` is also present in the list of capabilities).

``client``
  enable SASL authentication for SMTP client (for outgoing mail
  messages sent via relayhosts that require user authentication).

``sender_dependent``
  enable sender dependent SMTP client authentication
  (``client`` capability required).

``archive``
  BCC all mail (or mail from/to specified domains) passing
  through the SMTP server to an e-mail account on a local or remote server.

``postscreen``
  allows to enable postscreen support on port ``25`` independently of the
  ``mx`` capability.

``dnsbl``
  enables support for DNS blacklists in postscreen, automatically enables
  whitelists.

``dnswl``
  enables support for DNS whitelists in postscreen, without blacklists.

``test``
  enables the "soft_bounce" option and XCLIENT protocol extension for
  ``localhost`` (useful in mail system testing).

``defer``
  planned feature to defer mail delivery.

``auth``
  planned feature to enable user authentication.

Not all combinations of these capabilities will work correctly together.


.. _postfix_smtp_sasl_password_map:

postfix_smtp_sasl_password_map
------------------------------

A map of SMTP SASL passwords used in SMTP client authentication by Postfix.
You need to add ``client`` in Postfix capabilities to enable this feature.

Format of the password entries:

- *key*: remote SMTP server hostname or sender e-mail address
- *value*: username on the remote SMTP server

Example entries::

    postfix_smtp_sasl_password_map:
      'smtp.example.org': 'username'
      'user@example.org': 'username'
      'user@example.org': 'username@example.com'

Passwords are stored in a `secret`_ directory, in path::

    secret/credentials/{{ ansible_fqdn }}/postfix/smtp_sasl_password_map/{{ key }}/{{ value }}

If you do not define the passwords there, this role will generate
random passwords by default and store them there. You can use this
to your advantage by running debops once without defining the password
to let debops generate the right location automatically.

Passwords on the remote host are stored in::

    /etc/postfix/private_hash_tables/

To regenerate, change or add new passwords, you need to remove the ``*.lock``
files located in above directory.

.. _secret: https://github.com/debops/ansible-secret/


.. _postfix_dependent_lists:

postfix_dependent_lists
-----------------------

This variable can be used in Postfix dependency role definition to configure
additional lists used in Postfix main.cf configuration file. This variable
will be saved in Ansible facts and updated when necessary.

Examples
~~~~~~~~

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


.. _postfix_dependent_maincf:

postfix_dependent_maincf
------------------------

Here you can specify Postfix configuration options which should be enabled in
``/etc/postfix/main.cf`` using debops.postfix dependency role definition.
Configuration will be saved in Ansible facts and updated when necessary.

Examples
~~~~~~~~

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


.. _postfix_dependent_mastercf:

postfix_dependent_mastercf
--------------------------

This list can be used to configure services in Postfix master.cf using
Postfix dependency variables. Configured services will be saved in Ansible
facts and updated when necessary.

Parameters
~~~~~~~~~~

Optional parameters from master.cf:
- ``private``
- ``unpriv``
- ``chroot``
- ``wakeup``
- ``maxproc``

You can also specify ``capability`` or ``no_capability`` to define when
a particular service should be configured


Examples
~~~~~~~~

Minimal service using ``pipe`` command::

    postfix_dependent_mastercf:
      - service: 'mydaemon'
        type: 'unix'
        command: 'pipe'
        options: |
          flagsd=FR user=mydaemon:mydaemon
          argv=/usr/local/bin/mydaemon.sh ${nexthop} ${user}

