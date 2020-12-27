.. Copyright (C) 2015      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This `Ansible`_ role allows you to install and manage the `Dovecot`_
IMAP/POP3 server to allow remote access to your mail boxes. It integrates
with the `ansible-pki`_ role, so you can easily protect your access via
secure TLS connection.

Additionally it allows you to configure a `sieve`_ service which allows you
to store server-side rules for mail filtering.

.. _Ansible: https://www.ansible.com/
.. _Dovecot: https://dovecot.org/
.. _ansible-pki: https://github.com/debops/ansible-pki/
.. _sieve: http://sieve.info/
