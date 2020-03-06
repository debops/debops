.. Copyright (C) 2015 Patryk Ściborek <patryk@sciborek.com>
.. Copyright (C) 2015-2018 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2018 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This Ansible role manages GRUB configuration. It detects kernel parameters
which are currently set (probably during installation). Autodetected
parameters can be merged or overwritten by Ansible variables.
It can also enable both Linux kernel and GRUB serial console.

Parameter autodetection with values that contain spaces is not supported.

Additionally, this role allows you to configure password protection for GRUB.
