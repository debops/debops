.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Mosquitto <https://mosquitto.org/>`_ is an open source
`Message Queue Telemetry Transport (MQTT) <https://en.wikipedia.org/wiki/MQTT>`_
broker used in the `Internet of Things <https://en.wikipedia.org/wiki/Internet_of_things>`_
paradigm.

The ``debops.mosquitto`` Ansible role can be used to install and configure
Mosquitto on Debian/Ubuntu hosts. The role can use other DebOps roles to manage
firewall access to Mosquitto, publish Avahi services and configure an nginx
frontend for the Mosquitto WebSockets API.
