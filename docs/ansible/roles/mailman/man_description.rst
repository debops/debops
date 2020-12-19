.. Copyright (C) 2014-2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :ref:`debops.mailman` Ansible role can be used to create and manage mailing
lists using `GNU Mailman <https://list.org/>`_ service. The role is designed to
install and configure Mailman 3 using Debian packages, and will automatically
integrate with PostgreSQL or MariaDB database for configuration storage and
Postfix for SMTP services.

By default the role provides configuration for :ref:`debops.postfix` role to
configure the SMTP server integration, as well as :ref:`debops.nginx` role to
configure access to the web control panel.
