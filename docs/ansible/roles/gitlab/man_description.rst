.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.gitlab`` role can be used to install and manage a GitLab instance.
It supports automatic update of the currently installed version (when the role
is executed), as well as upgrade to a next stable GitLab release. You can deploy
the installation either on a single host, or a set of separate hosts, each one
with a different service (database, application, webserver).
