.. Copyright (C) 2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This role will ensure that the ``/proc`` filesystem is mounted with the
``hidepid=`` option enabled. `The 'hidepid=' option`__ can be used to hide
processes that don't belong to a particular user account.

.. __: https://wiki.archlinux.org/index.php/Security#hidepid
