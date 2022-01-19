.. Copyright (C) 2022 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2022 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

The `keepalived`__ service can be used to provide simple load balancing and
high availability services in a Linux cluster. The service uses the `Virtual
Router Redundancy Protocol`__ for communication between the nodes in a cluster
and can perform specified actions on the nodes - create or remove IP addresses,
start or stop services, and more.

.. __: https://keepalived.org/
.. __: https://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol

The ``debops.keepalived`` Ansible role can be used to install and configure the
:command:`keepalived` service on Debian and Ubuntu hosts. The role allows Jinja
expressions to be used in the :man:`keepalived.conf(5)` configuration file to
augment generated configuration files as needed.
