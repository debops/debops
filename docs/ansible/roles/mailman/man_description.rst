.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The :ref:`debops.mailman` Ansible role can be used to create and manage mailing
lists using `GNU Mailman <http://list.org/>`_ package.

By default the role provides configuration for :ref:`debops.postfix` role to
configure the SMTP server integration, as well as :ref:`debops.nginx` role to
configure access to the web control panel.
