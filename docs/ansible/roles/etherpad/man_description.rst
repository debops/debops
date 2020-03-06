.. Copyright (C) 2014-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015      Hartmut Goebel <h.goebel@crazy-compilers.com>
.. Copyright (C) 2015      Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2014-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Etherpad <https://en.wikipedia.org/wiki/Etherpad>`_ is a collaborative text
editor usable through a web browser. Documents can be edited by multiple people
in real time, shared and exported in different formats.

This role can be used to deploy and configure `Etherpad Lite <https://github.com/ether/etherpad-lite>`_,
a NodeJS version of Etherpad, on a Debian/Ubuntu host. The application can use
a MariaDB or SQLite database as a storage backend, and will be configured
behind a Nginx proxy as a frontend.
