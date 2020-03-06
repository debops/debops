.. Copyright (C) 2015 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015 DebOps <http://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`fcgiwrap`_ is a lightweight FastCGI server which can be set up behind
``nginx`` server to run CGI applications. This role allows you to setup
separate instances of ``fcgiwrap`` on different user accounts, each one
accessible through its own UNIX socket.

.. _fcgiwrap: https://github.com/gnosek/fcgiwrap
