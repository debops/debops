.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Miniflux`__ is a minimalist, web-based feed reader written in Go. It uses
PostgreSQL as the backend database and can be deployed behind nginx
webserver as a self-hosted application. The ``debops.miniflux`` Ansible role
can be used to deploy Miniflux on a host managed by DebOps.

.. __: https://miniflux.app/
