.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The :man:`systemd-networkd(8)` service is a part of the `systemd`__ project.
The service manages the runtime and on-disk configuration of the network
connections, physical and virtual network devices and their state in the
:man:`systemd-udevd(8)` subsystem.

.. __: https://www.freedesktop.org/wiki/Software/systemd/

The :ref:`debops.networkd` Ansible role can be used to generate and update
configuration of the :command:`systemd-networkd` service. Other parts of the
:command:`systemd` ecosystem are managed by separate Ansible roles.
