.. Copyright (C) 2015      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variables: configuration
================================

Some of ``debops.dovecot`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _dovecot_pop3_config_map:

dovecot_pop3_config_map
-----------------------

Configuration dictionary related to the POP3 protocol configuration. Please
to the :ref:`dovecot_imap_config_map` for a description of the dict layout.

.. _dovecot_pop3_listeners:

dovecot_pop3_listeners
----------------------

List of POP3 network listener names which will be used to decide which
default listeners to create. Their configuration can be customized via
:ref:`dovecot_pop3_config_map`.

.. _dovecot_auth_config_map:

dovecot_auth_config_map
-----------------------

Configuration dictionary related to user authentication when sending emails over
the SMTP protocol configuration. Postfix uses the `/var/spool/postfix/private/auth`
UNIX socket to communicate with Dovecot in order to authenticate an user, while
sending emails. See also `smtpd_sasl_type` and `smtpd_sasl_path` values in
:envvar:`postconf__postfix__dependent_maincf`.

Please refer to the :ref:`dovecot_imap_config_map` for a description of the dict
layout.

.. _dovecot_auth_listeners:

dovecot_auth_listeners
----------------------

List of AUTH unix listener names which will be created. The AUTH
listeners configuration works like the :ref:`dovecot_lmtp_listeners`.
Each listeners mentioned in :envvar:`dovecot_auth_listeners` must also be defined
in :ref:`dovecot_auth_config_map`.

Example
~~~~~~~

Enable ``sieve`` mail plugin with local mail delivery::

    dovecot_lda_config_map:

      protocol:
        mail_plugins: '$mail_plugins sieve'

.. _dovecot_managesieve_config_map:

dovecot_managesieve_config_map
------------------------------

Configuration dictionary related to the ManageSieve protocol configuration.
Please refer to the :ref:`dovecot_imap_config_map` for a description of the
dict layout.

.. _dovecot_managesieve_listeners:

dovecot_managesieve_listeners
-----------------------------

List of ManageSieve network listener names which will be used to decide
which default listeners to create when ``managesieve`` is enabled in
``dovecot_protocols``. Their configuration can be customized via
:ref:`dovecot_managesieve_config_map`.

Example
~~~~~~~

If you want to enable a second ManageSieve listener, you need to add
its name to the ``dovecot_managesieve_listeners`` list and define its
properties in the ``dovecot_managesieve_config_map``. For example to
bind a second listener to a specific address on port 2000::

    dovecot_managesieve_listeners: [ 'sieve', 'sieve_deprecated' ]

    dovecot_managesieve_config_map:

      login-service:
        inet_listeners:
          sieve_deprecated:
            address: 192.168.1.42
            port: 2000

.. _dovecot_postfix_transport:

dovecot_postfix_transport
-------------------------

LMTP socket name which will be configured in Postfix to send mails for
delivery. The value is a file system path relative to */var/spool/postfix*
Make sure there is a corresponding LMTP ``unix_listener`` defined in
:ref:`dovecot_lmtp_config_map` and enabled via :ref:`dovecot_lmtp_listeners`.
The LMTP transport target will only be configured in Postfix when 'lmtp'
is enabled in ``dovecot_protocols``.

For most people the default configuration will be sufficient.
