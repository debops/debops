.. Copyright (C) 2020 CipherMail B.V. <https://www.ciphermail.com/>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The :ref:`debops.mailman3` Ansible role can be used to manage the
`Mailman Suite <https://docs.mailman3.org/en/latest/>`_, which consists of
Mailman 3 Core, the Django-based Postorius web frontend and the Hyperkitty list
archiver.

The role provides integration with the :ref:`debops.ldap`, :ref:`debops.nginx`
and :ref:`debops.nginx` roles through dependent configuration.
