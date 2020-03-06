.. Copyright (C) 2015-2016 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2016 Robin Schneider <ypid@riseup.net>
.. Copyright (C) 2015-2016 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

The ``debops.libvirt`` role can be used to manage networks and storage pools
defined in `libvirt`_ virtualization service. It's designed to be used either
"locally", directly on a given host, or "remotely" from a central host through
the API.

To configure a host to provide the :program:`libvirtd` service you can use the
``debops.libvirtd`` role.

.. _libvirt: https://libvirt.org/
