.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@drybjed.net>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Nginx <https://nginx.org/>`_ is a fast and light webserver with extensible
configuration.

The ``debops.nginx`` role can be used to install and manage `nginx` configuration
for multiple websites at the same time. The server is configured using
inventory variables. This role can also be used as a dependency of another role
to configure a webserver for that role using dependency variables.
