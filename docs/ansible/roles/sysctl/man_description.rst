.. Copyright (C) 2015-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.sysctl`` Ansible role manages Linux kernel parameters.
It comes with kernel hardening and shared memory optimization enabled by
default.
The kernel hardening is ported from `hardening.os-hardening`__ for optimal
compatibility with DebOps.

.. __: https://github.com/hardening-io/ansible-os-hardening
