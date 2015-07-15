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

All you have to do to enable (Manage)Sieve in your Dovecot role is to add
it to the ``dovecot_protocols`` list::

    dovecot_protocols: [ 'imap', 'imaps', 'managesieve' ]

The ManageSieve protocol listens on port 4190 and requires STARTTLS for
authentication. You can restrict access to this port by explicitly listing
the networks or hosts which are allowed to connect::

    dovecot_protocol_map:
      managesieve:
        allow: [ '192.168.1.0/24' ]

The sieve filter rules are applied before delivering the mail to the user's
mailbox. There are various ways for mail delivery but only a few of them
respect the sieve filters. By default DebOps would simply use postfix to
write the mail. However, postfix doesn't know anything about sieve.
Therefore you have to manually add the following configuration to each
user's ``~/.forward`` file, to hook-in the Dovecot LDA (local delivery
agent)::

    | "/usr/lib/dovecot/dovecot-lda"

The Dovecot LDA would then deliver the mail after enquiring the sieve
files.

Another possibility would be to tell Postfix to forward the mail to the
Dovecot LMTP (local mail transfer protocol) service which also supports
sieve filtering. Unfortunately support for this hasn't been added to
the corresponding DebOps rules yet.

By default the Dovecot sieve plugin will store the user defined rules as
plain text files in the ``~/sieve/`` folder. They can be managed directly
via file system, by a mail client which supports the ManageSieve protocol
or alternatively by a tool like `sieve-connect`_.

.. _sieve-connect: https://github.com/philpennock/sieve-connect/
