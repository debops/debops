.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2016-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Introduction
============

.. include:: includes/all.rst

Snapper can manage snapshots for the following filesystems and volume managers:

* btrfs
* ext4
* lvm2

This role allows to setup and configure snapper with Ansible.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.3``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops-contrib.snapshot_snapper

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
