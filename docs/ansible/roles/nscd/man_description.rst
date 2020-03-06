.. Copyright (C) 2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The Name Service Cache Daemon is a local service which caches NSS database
information from remote sources like LDAP, Active Directory or NIS. The service
is useful in combination with the :command:`nslcd` (managed by the
:ref:`debops.nslcd` role) to lower the number of queries to the remote
databases and make system oprations faster.

The ``debops.nscd`` Ansible role supports two flavors of the caching service,
the original :command:`nscd` implemented by GNU ``libc`` library, as well as
its drop-in replacement, :command:`unscd`, created by the BusyBox project. The
:command:`unscd` version is installed by default.
