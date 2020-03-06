.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The Journal, part of the `systemd`__ project, is a syslog replacement. On
systems that use :command:`systemd` as the init daemon, the
:command:`systemd-journald` service takes care of receiving, storing and
routing the log messages received via the :file:`/dev/log` device, the
:man:`logger(1)` command or from services managed by the :command:`systemd`
init daemon.

.. __: https://www.freedesktop.org/wiki/Software/systemd/

The ``debops.journald`` Ansible role can be used to manage the Journal
configuration, enable or disable persistent log storage and configure Forward
Secure Sealing on the managed hosts.
