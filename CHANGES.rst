Changelog
=========

v0.1.0
------

*Unreleased*

- Add Changelog. [drybjed]

- Change default TFTP root directory to ``/srv/tftp/`` to be compatible with
  defaults from ``tftpd-hpa`` package. [drybjed]

- Switch from PXE boot to iPXE boot and drop support for installation of Debian
  Netboot Installer. Custom menu will be handled by a separate role. [drybjed]

