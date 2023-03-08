.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The `systemd`__ project is a system and service manager, a replacement for the
traditional :file:`/bin/init` daemon started by the kernel after the boot
process is complete. :command:`systemd` focuses on the intermediate layer
between the "kernel space" and "userspace", so called "system" layer. The
project itself is composed from multiple separate services which can be enabled
or disabled as needed.

.. __: https://www.freedesktop.org/wiki/Software/systemd/

The :ref:`debops.systemd` Ansible role focuses on management of the
:command:`systemd` service itself; other Ansible roles included in the DebOps
project can be used to manage disparate components like :command:`journald` via
the :ref:`debops.journald` role. This role manages the "system" instance of
:command:`systemd`, as well as the global configuration of the
:command:`systemd --user` instances and the configuration of the
:command:`systemd-logind` login manager.
