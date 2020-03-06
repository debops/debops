.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The `Postscreen <http://www.postfix.org/POSTSCREEN_README.html>`_ Postfix
service can be enabled to filter out undesired SMTP clients on initial
connection to the mail server. Postscreen uses certain criteria (static
white/blacklist, DNS Block List queries, communication analysis) to allow or
deny connections for a given SMTP client.

This role can be used to enable and configure Postscreen in a Postfix
installation managed by the :ref:`debops.postfix` Ansible role. It does not configure
Postfix directly on its own.
