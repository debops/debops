.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

THe :man:`systemd-timesyncd(8)` service is a lightweight SNTP and NTP (Network
Time Protocol) client developed as a part of the `systemd`__ project. It
provides time synchronization with NTP server network on hardware and
virtualized hosts.

.. __: https://www.freedesktop.org/wiki/Software/systemd/

The :ref:`debops.timesyncd` Ansible role can be used to configure the
:command:`systemd-timesyncd` service. It will detect presence of alternative
NTP clients/servers installed on the host and back off when they are detected,
so that users can easily switch to a different service provider if they wish.
