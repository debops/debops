Default variables: configuration
================================

Some of ``debops.dovecot`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _dovecot_protocols:
.. _dovecot_imap_config_map:
.. _dovecot_imap_listeners:
.. _dovecot_pop3_config_map:
.. _dovecot_pop3_listeners:
.. _dovecot_lda_config_map:
.. _dovecot_managesieve_config_map:
.. _dovecot_managesieve_listeners:


dovecot_protocols
-----------------

List of protocols which should be installed and enabled. So far supported are:
``imap``, ``imaps``, ``pop3``, ``pop3s``, ``managesieve``


Examples
~~~~~~~~

Possible configuration options for enabling IMAP:

+---------------------------------+------------------------+------------------+
+ Service                         + ``dovecot_protocols``  | ``dovecot_pki``  +
+=================================+========================+==================+
+ Port 143 (plain)                + ``[ 'imap' ]``         | ``False``        |
+---------------------------------+------------------------+------------------+
+ Port 143 (StartTLS)             + ``[ 'imap' ]``         | ``True``         |
+---------------------------------+------------------------+------------------+
+ Port 143 (StartTLS) + 995 (SSL) + ``[ 'imap', 'imaps']`` | ``True``         |
+---------------------------------+------------------------+------------------+


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


.. _Dovecot Login Process: http://wiki2.dovecot.org/LoginProcess
.. _Dovecot inet_listeners: http://wiki2.dovecot.org/Services#inet_listeners
.. _Dovecot IMAP Service: http://wiki2.dovecot.org/Services#imap.2C_pop3.2C_managesieve


dovecot_imap_listeners
----------------------

List of IMAP network listener names which will be used to decide which
default listeners to create. Their configuration can be customized via
:ref:`dovecot_imap_config_map`. This value usually shouldn't be changed.


dovecot_pop3_config_map
-----------------------

Configuration dictionary related to the POP3 protocol configuration. Please
to the :ref:`dovecot_imap_config_map` for a description of the dict layout.


dovecot_pop3_listeners
----------------------

List of POP3 network listener names which will be used to decide which
default listeners to create. Their configuration can be customized via
:ref:`dovecot_pop3_config_map`. This value usually shouldn't be changed.


dovecot_lda_config_map
-----------------------

Configuration dictionary related to the Dovecot LDA protocol configuration.
The only valid key is ``protocol`` which references a YAML dict defining the
``protocol lda {}`` section. The ``protocol`` dict then accepts the upstream
Dovecot configuration options such as ``mail_plugins``.


Example
~~~~~~~

Enable ``sieve`` mail plugin with local mail delivery::

    dovecot_lda_config_map:

        protocol:
            mail_plugins: [ 'sieve' ]


dovecot_managesieve_config_map
------------------------------

Configuration dictionary related to the ManageSieve protocol configuration.
Please refer to the :ref:`dovecot_imap_config_map` for a description of the
dict layout.


dovecot_managesieve_listeners
-----------------------------

List of ManageSieve network listener names which will be used to decide
which default listeners to create when ``managesieve`` is enabled in
:ref:`dovecot_protocols`. Their configuration can be customized via
:ref:`dovecot_managesieve_config_map`. This value usually shouldn't be
changed.

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
