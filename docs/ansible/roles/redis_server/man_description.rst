.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Redis <https://redis.io/>`__ is an in-memory key/value store, usable as
a persistent database, cache or a message broker.

The ``debops.redis_server`` Ansible role can be used to install and manage
Redis on Debian/Ubuntu hosts. Role supports management of multiple Redis
instances on a single host and is designed to cope with modifications done to
Redis configuration files at runtime.
