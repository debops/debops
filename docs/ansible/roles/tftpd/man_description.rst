.. Copyright (C) 2015-2019 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2015-2019 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Description
===========

This Ansible role can configure a standalone TFTP server using the
:command:`tftpd-hpa` daemon. The TFTP server can be used to serve files for
embedded devices or serve iPXE files from :ref:`debops.ipxe` role to other
hosts on the network, allowing for network boot and OS installation.
