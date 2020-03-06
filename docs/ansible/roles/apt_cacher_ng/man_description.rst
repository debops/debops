.. Copyright (C) 2016-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

Ansible role to install and manage Apt-Cacher NG.
Apt-Cacher NG is a caching HTTP proxy for downloading software packages.  This
role sets up the Apt-Cacher NG server in your network and allows clients to use
the proxy.  Only the proxy server is setup by this role.

The following options are available to get clients to use the Apt-Cacher NG server:

* Advanced Package Tool: :ref:`debops.apt_proxy`
