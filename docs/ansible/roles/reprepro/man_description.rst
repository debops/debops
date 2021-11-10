.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The ``reprepro`` Debian package is an `APT repository manager`__. It can be
used to create and maintain APT repositories for Debian or Ubuntu operating
systems and their derivatives. The repositories managed by :command:`reprepro`
can be used to distribute third-party software packages or create local mirrors
of official Debian or Ubuntu repositories.

.. __: https://wiki.debian.org/DebianRepository/SetupWithReprepro

The :ref:`debops.reprepro` role uses the :command:`reprepro` package to
maintain multiple sets of APT repositories, with optional authentication and
access restrictions.
