.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`DokuWiki`_ is an easy to use, file-based wiki written in PHP5.
``debops.dokuwiki`` role installs this wiki on a specified host with nginx
as a webserver (using :ref:`debops.nginx`). You can optionally
configure multiple DokuWiki instances with shared base installation using
`DokuWiki vhost farm`_ mode.

.. _DokuWiki: https://www.dokuwiki.org/
.. _DokuWiki vhost farm: https://www.dokuwiki.org/farms
