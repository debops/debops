.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.machine`` Ansible role manages basic information about a given
host located in the :file:`/etc/machine-info` configuration file, as well as
static and dynamic Message Of The Day (MOTD) shown after login, and the
contents of the :file:`/etc/issue` file displayed on the `system console`__.

.. __: https://en.wikipedia.org/wiki/System_console
