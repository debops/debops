Guides and examples
===================

Using maildir mail storage format
---------------------------------

If you want to use maildir instead of mbox you first have to make sure,
that your mail delivery agent is storing the incoming mails in the maildir
format. If you are using the `ansible-postfix`_ role, this can be achieved
by setting the following configuration:

.. _ansible-postfix: https://github.com/debops/ansible-postfix

* Make sure ``local`` is in your ``postfix`` capabilities list

* Set the postfix ``home_mailbox`` configuration value to the desired path.
  It must end with a slash **/** to indicate the maildir format::

    postfix_local_maincf: |
      home_mailbox = Maildir/

This example will store the mails in the ``Maildir/`` folder within the user's
home directory. You can make dovecot looking for this maildir by setting::

    dovecot_mail_location: 'maildir:~/Maildir'

The ``dovecot_mail_location`` variable corresponds to the ``mail_location``
statement in the dovecot configuration file, so you can also set much more
advanced values. Check the dovecot `mail_location`_ documentation for more
examples.

.. _mail_location: http://wiki2.dovecot.org/MailLocation/


Enable server-side mail filtering with sieve
--------------------------------------------

`Sieve`_ is a programming language to define mail filtering rules. The
rules are stored as text files on the mail server and can be managed by
a client via `ManageSieve`_ network protocol. Dovecot provides sieve support
via Pigeonhole sieve interpreter.

.. _Sieve: http://wiki2.dovecot.org/Pigeonhole/Sieve/
.. _ManageSieve: http://wiki2.dovecot.org/Pigeonhole/ManageSieve/

To enable the ManageSieve protocol in your Dovecot role you have to add
it to the ``dovecot_protocols`` list::

    dovecot_protocols: [ 'imap', 'managesieve' ]

It will create a network listener on port 4190 which requires STARTTLS for
authentication. You can restrict access to this port by explicitly listing
the networks or hosts which are allowed to connect::

    dovecot_managesieve_config_map:
      login-service:
        inet_listener:
          sieve:
            allow: [ '192.168.1.0/24' ]

By default every host can connect.

The sieve filter rules are applied before delivering the mail to the user's
mailbox. There are various ways for mail delivery but only a few of them
respect the sieve filters. By default DebOps would simply use Postfix to
write the mail. However, Postfix doesn't know about sieve. Therefore you
have to manually add the following configuration to each user's ``~/.forward``
file, to hook-in the Dovecot LDA (local delivery agent):

.. code-block:: none

    | "/usr/lib/dovecot/dovecot-lda"

To enable the sieve filter with the Dovecot LDA you further have to enable
the plugin for the corresponding protocol::

    dovecot_lda_config_map:
      protocol:
        mail_plugins: '$mail_plugins sieve'

The Dovecot LDA would then deliver the mail after enquiring the sieve
files. Alternatively mail can be delivered via LMTP protocol, which also
supports sieve filtering (see section below).

By default the Dovecot sieve plugin will store the user defined rules as
plain text files in the ``~/sieve/`` folder. They can be managed directly
via file system, by a mail client which supports the ManageSieve protocol
or alternatively by a tool like `sieve-connect`_.

.. _sieve-connect: https://github.com/philpennock/sieve-connect/


Enable LMTP to deliver mails from Postfix
-----------------------------------------

`LMTP`_ is a reliable, scalable and secure protocol to deliver mails
into local mail boxes. It is implemented by Dovecot as an alternative
to the Dovecot LDA and also supports most mail plugins, such as
sieve filtering.

It can be enabled by adding it to the ``dovecot_protocols`` list. E.g.::

    dovecot_protocols: [ 'imap', 'lmtp' ]

Without further configuration, this will instruct DebOps to setup a LMTP
unix socket, which is then used by Postfix for mail delivery. In this
case Postfix will be automatically added as a dependency and configured
accordingly.

To enable mail plugins specifically to LMTP only, they can be added to
the ``mail_plugins`` parameter in :ref:`dovecot_lmtp_config_map`::

    dovecot_lmtp_config_map:
      protocol:
        mail_plugins: '$mail_plugins sieve'

In case your Postfix is not running on the same machine, you can enable
a network socket where the LMTP service is listening on. E.g.::

    dovecot_lmtp_listeners: [ 'lmtp' ]

Then define its properties::

    dovecot_lmtp_config_map:
      service:
        inet_listener:
          lmtp:
            port: 24
            allow: [ '192.168.1.0/24' ]
            address: 192.168.1.123

This would bind LMTP to the local address 192.168.1.123 on port 24.
Additionally, access is restricted by `ansible-ferm`_ to the given
network. When using the LMTP network socket, you have to configure
Postfix independently by setting e.g.::

    postfix_local_maincf: |
      mailbox_transport = lmtp:inet:192.168.1.123:24


.. _LMTP: http://wiki2.dovecot.org/LMTP
.. _ansible-ferm: https://github.com/debops/ansible-ferm
