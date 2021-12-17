.. Copyright (C) 2015      Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
.. Copyright (C) 2017-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`dovecot` daemon, maintained by the `Dovecot Project`__, is a
modern IMAP and POP3 email server for Linux/UNIX-like systems, written with
security primarily in mind. Dovecot is an excellent choice for both small and
large installations. It’s fast, simple to set up, requires no special
administration and it uses very little memory.

.. __: https://www.dovecot.org/

The ``debops.dovecot`` Ansible role can be used to configure the
:command:`dovecot` service on a host and to automatically setup
various auxiliary roles, such as :ref:`debops.pki` for SSL/TLS encryption.
