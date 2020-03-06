.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Redis <https://redis.io/>`__ is an in-memory key/value store, usable as
a persistent database, cache or a message broker.
`Redis Sentinel <https://redis.io/topics/sentinel>`_ manages the failover and
high availability of a Redis cluster.

The ``debops.redis_sentinel`` Ansible role can be used to install and manage
multiple Redis Sentinel instances on Debian/Ubuntu hosts.
