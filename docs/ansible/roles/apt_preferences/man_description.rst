.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`APT preferences`_ can be used to influence package selection performed by APT
during installation or upgrades. You can for example tell APT that you prefer
packages from certain repositories or want to hold a package on a particular
version no matter what (among other things).

By default, if you don't specify a version or provide a custom pin configuration,
``debops.apt_preferences`` role will configure the specified packages to be
installed from the backports repository of the current OS release.

.. _APT preferences: https://wiki.debian.org/AptPreferences
