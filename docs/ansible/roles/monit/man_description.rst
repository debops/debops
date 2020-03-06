.. Copyright (C) 2014      Nick Janetakis <nick.janetakis@gmail.com>
.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Monit <https://mmonit.com/monit/>`_ is a service monitoring daemon. It can be
used to monitor processes, files, system and remote hosts, and if necessary,
take configured actions when specific parameters change, like restarting
services and notifying the system administrator.

This role can be used to configure Monit on a host. It will automatically
detect selected services and configure checks for them.
