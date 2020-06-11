.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.tzdata`` Ansible role helps manage the time zone on Debian/Ubuntu
hosts. The role will make sure that services affected by time zone changes
(:command:`cron`, :command:`rsyslog`) will be restarted if needed.

The role also provides the ``ansible_local.tzdata.timezone`` Ansible local fact
with the host time zone specified in the ``Area/Zone`` format required in some
configuration files.
