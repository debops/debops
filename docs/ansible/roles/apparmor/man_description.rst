.. Copyright (C) 2022 David Härdeman <david@hardeman.nu>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`AppArmor`__ is a Linux kernel Security Module (`LSM`) which provides
`mandatory access control`__.

Programs are restricted on the basis of `profiles`, which are traditionally
stored under :file:`/etc/apparmor.d/`, using filenames which correspond to
the path to the binary being protected by the profile
(:file:`/usr/bin/foobar` → :file:`/etc/apparmor.d/usr.bin.foobar`).

Profiles can be configured in different modes: ``enforce``, ``disabled``, or
``complain`` (log, but don't enforce).

This role is primarily geared towards allowing other roles to perform
customizations of existing profiles, and allowing administrators to
selectively enable/disable profiles.

.. __: https://apparmor.net/
.. __: https://en.wikipedia.org/wiki/Mandatory_access_control
