.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :command:`at` and :command:`batch` commands can be used to compliment :program:`cron` and run
one-off tasks either at a specified time, or when the host CPU utilization is on
a low enough level.

The ``debops.atd`` role can be used to configure the :program:`atd` service, including
randomized load average threshold and randomized time between batch job
execution, as well as access control to the :command:`at` and ``batch`` commands by
the users.
