.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015      Hartmut Goebel <h.goebel@crazy-compilers.com>
.. Copyright (C) 2015-2019 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This role installs a NextCloud__ or ownCloud__ instance on a specified host, either with
SQLite, MySQL, MariaDB or PostgreSQL database as a backend and an Nginx
or Apache webserver as a frontend.

.. __: https://nextcloud.com/
.. __: https://en.wikipedia.org/wiki/OwnCloud

Nextcloud will be installed using the upstream tarballs. ownCloud will be installed as package coming directly from upstream.

Note that Nginx is `not officially supported by ownCloud nor NextCloud
<https://github.com/debops/ansible-owncloud/issues/49>`_ but it is community
supported and should work without problems. Apache is supported by the role but
not yet used by default and not very well tested.

**Features:**

* Support for LDAP using the :ref:`debops.ldap` Ansible role.
* In memory caching using Redis for file locking and APCu.
* Theming support (only tested with ownCloud 10).
* Extensive configuration options via Ansible’s inventory.
* Fully automated ownCloud security updates. `Not yet enabled by default nor tested with ownCloud 10 <https://github.com/debops/ansible-owncloud/issues/28>`_.
