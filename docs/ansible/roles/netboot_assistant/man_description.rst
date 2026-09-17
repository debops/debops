.. Copyright (C) 2026 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Description
===========

Debian supports `installation through PXE network booting`__. One way to
implement this is to use a DHCP server and TFTP server to offer Debian Installer
images to hosts over the network.

.. __: https://wiki.debian.org/PXEBootInstall

To maintain the local Debian Installer images and update them on point
releases, users can utilize the `di-netboot-assistant`__ Debian package. It
contains the scripts and logic to download specific Debian or Ubuntu netboot
images and veriy their authenticity, as well as add optional non-free firmware
to be available in the installer.

.. __: https://wiki.debian.org/DebianInstaller/NetbootAssistant

The ``debops.netboot_assistant`` Ansible role provides a convenient way to use
the package and configure a set of Debian Installer "netinst" images on a TFTP
server. The role also includes a refresh script which will handle the planned
point releases as they occur so that the images can be kept up to date
automatically.

The role integrates with the :ref:`debops.ipxe` role to provide a convenient
`iPXE`__ boot menu and :ref:`debops.preseed` role which manages a set of
`Debian Preseed`__ scripts for the installer to use.

.. __: https://ipxe.org/
.. __: https://wiki.debian.org/DebianInstaller/Preseed
