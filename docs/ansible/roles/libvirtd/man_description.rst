.. Copyright (C) 2015-2017 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2017 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2017 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

``debops.libvirtd`` Ansible role manages the `libvirtd`_ daemon on
a virtualization host (server side). It will automatically install QEMU KVM
support on any host that is not a KVM guest, to allow for easy deployment of
KVM virtual machines.

Configuration of :program:`libvirtd` instance (local or remote) can be performed using
:ref:`debops.libvirt` role, which uses the ``libvirt`` API to manage the server.

.. _libvirtd: https://libvirt.org/
