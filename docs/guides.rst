Guides and examples
===================

Using maildir mail box format
-----------------------------

If you want to use maildir instead of mbox you first have to make sure,
that your mail delivery agent is storing the incoming mails in the maildir
format. If you are using the `ansible-postfix`_ role, this can be achieved
by setting the following configuration:

* Make sure ``local`` is in your ``postfix`` capabilities list

* Set the postfix ``home_mailbox`` configuration value to the desired path.
  The path must end with a slash **/** to indicate the maildir format:

    postfix_local_maincf: |
      home_mailbox = Maildir/

This example will store the mails in the ``Maildir/`` folder within the users
home directory. You can make dovecot looking for this maildir by setting:

    dovecot_mail_location: 'maildir:~/Maildir'


.. _ansible-postfix: https://github.com/debops/ansible-postfix
