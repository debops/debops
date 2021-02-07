.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The `extrepo`__ Debian package provides an easy way to manage APT sources
external to the Debian main archives. The `list of supported APT sources`__ is
curated outside of the normal Debian release cycle and contains details about
popular third-party APT repositories maintained by software vendors.

.. __: https://packages.debian.org/sid/extrepo
.. __: https://salsa.debian.org/extrepo-team/extrepo-data

The ``debops.extrepo`` Ansible role can be used to manage third-party APT
repositories via Ansible using the ``extrepo`` package. The role is written as
complimentary to the :ref:`debops.keyring` role which provides a similar
functionality.
