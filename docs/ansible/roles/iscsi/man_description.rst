.. Copyright (C) 2015 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

`Open-iSCSI`_ is a Linux iSCSI Initiator which can be used to connect to iSCSI
Targets to access block storage devices remotely as if they were connected
locally.

``debops.iscsi`` Ansible role allows you to configure the initiator, targets,
as well as create LVM Volume Groups from presented iSCSI LUNs and manage LVM
Logical Volumes.

.. _Open-iSCSI: http://open-iscsi.org/
