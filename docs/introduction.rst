Introduction
============

This `Ansible`_ role allows you to install and manage the ``dovecot``
IMAP/POP3 server to allow remote access to your mail boxes. It integrates
with the ``dovecot.pki`` role, so you can easily protect your access via
secure TLS connection.

Additionally it allows you to configure a ``sieve`` service which allows you
to save server-side rules for mail filtering.

.. _Ansible: http://ansible.com/
.. _dovecot: http://dovecot.org/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
