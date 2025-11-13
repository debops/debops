.. Copyright (C) 2025 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2025 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

`pgBadger`__ is a PostgreSQL log parser and analyzer, which can be used to
generate detailed summaries of PostgreSQL logs either locally or via remote SSH
connections in various formats.

The :ref:`debops.pgbadger` role can be used to install and manage the
:command:`pgbadger` Debian package, and use it to generate HTML reports from
local or remote hosts via SSH. The default configuration is designed for
publishing HTML reports using a webserver and allows for extensive
configuration.

.. __: https://pgbadger.darold.net/
