Introduction
============

This `Ansible`_ role allows you to install and manage the `Dovecot`_
IMAP/POP3 server to allow remote access to your mail boxes. It integrates
with the `ansible-pki`_ role, so you can easily protect your access via
secure TLS connection.

Additionally it allows you to configure a `sieve`_ service which allows you
to store server-side rules for mail filtering.

.. _Ansible: http://ansible.com/
.. _Dovecot: http://dovecot.org/
.. _ansible-pki: https://github.com/debops/ansible-pki/
.. _sieve: http://sieve.info/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
