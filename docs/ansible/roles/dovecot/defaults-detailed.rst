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

.. _dovecot_postfix_lmtp_transport:

dovecot__postfix_lmtp_transport
-------------------------

LMTP socket name which will be configured in Postfix to send mails for
delivery. The value is a file system path relative to */var/spool/postfix*
The LMTP transport target will only be configured in Postfix when 'lmtp'
is enabled in ``dovecot__features``.

For most people the default configuration will be sufficient.
