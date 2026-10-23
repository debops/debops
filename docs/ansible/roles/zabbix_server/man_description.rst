.. Copyright (C) 2026 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Zabbix <https://www.zabbix.com/>`_ is an open source monitoring solution for
networks, servers, virtual machines and cloud services. The ``debops.zabbix_server``
Ansible role installs and configures the Zabbix Server daemon, its PostgreSQL
database schema and the PHP web frontend, and manages global Zabbix objects
(media types, actions, users, custom templates) via the Zabbix JSON-RPC API.
It is meant to be used together with the :ref:`debops.zabbix_agent` role,
which configures Zabbix Agents on monitored hosts and can self-register them
in Zabbix Server managed by this role.
