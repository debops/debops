.. Copyright (C) 2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.nsswitch`` Ansible role can be used to configure the Name Service
Switch using the :file:`/etc/nsswitch.conf` configuration file. The role can be
used as a dependency of another Ansible role to allow management of NSS
services after they have been configured. System administrators can use this
role to enable or disable NSS services conditionally or change the preferred
order of the NSS services.
