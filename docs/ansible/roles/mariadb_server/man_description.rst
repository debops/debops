.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

MariaDB__ is a popular relational SQL database that was forked from MySQL
server. Ansible roles :ref:`debops.mariadb` and ``debops.mariadb_server`` allow
you to manage a MariaDB server and / or access it remotely from other hosts.

``debops.mariadb_server`` role is the "server" part - it installs
``mariadb-server`` Debian package, and configures access to the database from
local ``root`` account. After that, you can use :ref:`debops.mariadb` role to
manage databases and user accounts on the server.

.. __: https://en.wikipedia.org/wiki/Mariadb
