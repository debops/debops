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

.. _dovecot_imap_config_map:

dovecot_imap_config_map
-----------------------

Configuration dictionary related to the IMAP protocol configuration. Every
configuration key is optional and overwrites the default values implicitly
used by Dovecot. Each section ``service imap-login``, ``service imap`` and
``protocol imap`` is defined as a YAML dict with the corresponding key:

``login-service``
  Configuration settings under this key will go into the ``service imap-login {}``
  section which defines the pre-login process handling. Possible keys are
  ``inet_listener`` and upstream Dovecot options such as ``service_count`` or
  ``process_min_avail``. More information about the login setup can be found at
  the `Dovecot Login Process`_ page.

  ``inet_listener``
    Will create a network listener definition. Accepts further YAML dicts with
    the listener name as key.

    The listener name itself must reference a dict defining listener properties
    such as ``port`` (network port), ``allow`` (address/subnet restrictions) or
    ``address`` (listen address). More information about the ``inet_listener``
    setup can be found at the `Dovecot inet_listeners`_ page.

  ``unix_listener``
    Will create a Unix socket definition. The key name of the listeners corresponds
    to the socket path.

    The listener name itself must reference a dict defining socket properties such
    as ``owner`` (socket owner), ``group`` (socket group) or ``mode`` (access mode).
    More information about the ``unix_listener`` setup can be found at the
    `Dovecot unix_listeners`_ page.

``service``
  Configuration settings under this key will go into the ``service imap {}``
  section which defines the post-login process handling. Possible keys are the
  upstream Dovecot options such as ``process_limit`` or ``vsz_limit``. More
  information about the IMAP service options can be found at the `Dovecot IMAP Service`_
  page.

``protocol``
  Configuration settings under this key will go into the ``protocol imap {}``
  section which defines general protocol behaviour. Possible keys are the
  upstream Dovecot options such as ``mail_max_userip_connections`` or
  ``mail_plugins``.


Example
~~~~~~~

Restrict access to the IMAP service to 192.168.1.0/24. Always keep a process
waiting for more connections, restrict maximal number of IMAP processes to
512 and allow 15 IMAP connections for each user::

    dovecot_imap_config_map:

      login-service:
        inet_listener:
          imap:
            access: [ '192.168.1.0/24' ]

        process_min_avail: 1

      service:
        process_limit: 512

      protocol:
        mail_max_userip_connections: 15


.. _Dovecot Login Process: https://wiki2.dovecot.org/LoginProcess
.. _Dovecot inet_listeners: https://wiki2.dovecot.org/Services#inet_listeners
.. _Dovecot unix_listeners: https://wiki2.dovecot.org/Services#unix_listeners_and_fifo_listeners
.. _Dovecot IMAP Service: https://wiki2.dovecot.org/Services#imap.2C_pop3.2C_submission.2C_managesieve

.. _dovecot_imap_listeners:

dovecot_imap_listeners
----------------------

List of IMAP network listener names which will be used to decide which
default listeners to create. Their configuration can be customized via
:ref:`dovecot_imap_config_map`.

Examples
~~~~~~~~

Possible configuration options for enabling IMAP:

+---------------------------------+-----------------------+----------------------------+------------------+
| Service                         | ``dovecot_protocols`` | ``dovecot_imap_listeners`` | ``dovecot_pki``  |
+=================================+=======================+============================+==================+
| Port 143 (plain)                | ``[ 'imap' ]``        | ``[ 'imap' ]``             | ``False``        |
+---------------------------------+-----------------------+----------------------------+------------------+
| Port 143 (StartTLS)             | ``[ 'imap' ]``        | ``[ 'imap' ]``             | ``True``         |
+---------------------------------+-----------------------+----------------------------+------------------+
| Port 143 (StartTLS) + 995 (SSL) | ``[ 'imap' ]``        | ``[ 'imap', 'imaps' ]``    | ``True``         |
+---------------------------------+-----------------------+----------------------------+------------------+
| Port 995 (SSL)                  | ``[ 'imap' ]``        | ``[ 'imaps' ]``            | ``True``         |
+---------------------------------+-----------------------+----------------------------+------------------+

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

.. _dovecot_lmtp_config_map:

dovecot_lmtp_config_map
-----------------------

Configuration dictionary related to the LMTP protocol configuration. Please
refer to the :ref:`dovecot_imap_config_map` for a description of the dict
layout.

In contrast to the other protocol maps, LMTP ``inet_listeners`` must always
be listed in ``dovecot_lmtp_config_map`` and define the ``port`` property,
as Dovecot doesn't define a default port for LMTP network listeners.

.. _dovecot_lmtp_listeners:

dovecot_lmtp_listeners
----------------------

List of LMTP network and unix listener names which will be created. The LMTP
listeners configuration works a bit different from other network protocols.
Each listeners mentioned in ``dovecot_lmtp_listeners`` must also be defined
in :ref:`dovecot_lmtp_config_map`.

.. _dovecot_lda_config_map:

dovecot_lda_config_map
-----------------------

Configuration dictionary related to the Dovecot LDA protocol configuration.
The only valid key is ``protocol`` which references a YAML dict defining the
``protocol lda {}`` section. The ``protocol`` dict then accepts the upstream
Dovecot configuration options such as ``mail_plugins``.

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

.. _dovecot_mailbox_definitions:

dovecot_mailbox_definitions
---------------------------

Configuration dictionary for mailbox specific settings. Valid keys are
``name`` (mandatory), ``comment``, ``special_use``, ``auto``, ``imap_comment``
and ``state``.

``name`` is the name of the mailbox. ``comment`` includes a comment in the
generated configuration file. ``state`` can either be ``comment`` (in which
case the mailbox entry will be included in the generated configuration file
but commented out) or ``present`` (in which case the mailbox entry will be
included in the generated configuration, this is also the default if ``state``
is not set). Other values will lead to the mailbox entry being silently
ignored.

``auto`` controls whether a mailbox with the given ``name`` will be
automatically created and whether users will be automatically subscribed.
Possible values are ``no`` (don't create automatically, the default),
``create`` (autocreate but don't autosubscribe) and ``subscribe``
(autocreate and autosubscribe).

``special_use`` marks a mailbox with special-use flags (see 
`RFC6154`_) which assist mail clients in autoconfiguring
new mail accounts. A mailbox can be tagged with one or more special-use
flags (defined as a string or list of strings), but mail clients are unlikely
to recognize anything else than the standard ones, which are:

\All
  This (virtual) mailbox presents all messages in the user's message store.
\Archive
  This mailbox is used to archive messages.
\Drafts
  This mailbox is used to hold draft messages.
\Flagged
  This (virtual) mailbox presents all messages in the
  user's message store marked with the IMAP \Flagged flag.
\Important
  This (virtual) mailbox presents all messages in the
  user's message store deemed important to the user.
\Junk
  This mailbox is where messages deemed to be junk mail
  are held.
\Sent
  This mailbox is used to hold copies of messages that
  have been sent.
\Trash
  This mailbox is used to hold messages that have been
  deleted.

``imap_comment`` adds a comment for a mailbox which is made available to
mail clients via the IMAP METADATA protocol.

.. _RFC6154: https://datatracker.ietf.org/doc/html/rfc6154#page-4
