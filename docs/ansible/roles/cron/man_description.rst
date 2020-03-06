.. Copyright (C) 2016-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.cron`` Ansible role can be used to manage :program:`cron` jobs
through Ansible inventory. You can define :program:`cron` jobs at different
levels of Ansible inventory (all hosts, a group of hosts, specific hosts) and
manage custom files or scripts required by the jobs.
