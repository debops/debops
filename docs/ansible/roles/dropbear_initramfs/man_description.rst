.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2017-2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.dropbear_initramfs`` role allows you to setup SSH access
to the initramfs prior to the root filesystem being mounted using Dropbear as
SSH server.

This can be used to unlock a full disk encrypted host remotely via SSH.
