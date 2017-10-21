Changelog
=========

v0.1.3
------

*Released: 2015-07-12*

- Change Debian Installer mirror URL to current HTTP redirector. [drybjed]

- Add support for local Debian netinst installation with optional (enabled by
  default) non-free firmware added to ``initrd.gz`` to help install Debian on
  systems that require non-free firmware. Installer uses PXE and TFTP.
  [drybjed]

- Add a menu option in iPXE Boot Menu to switch to local PXE Boot Menu.
  [drybjed]

v0.1.2
------

*Released: 2015-04-26*

- Add an option to set custom Debian-Installer boot parameters during iPXE
  boot. [drybjed]

- Prefer ``ipxe`` package from ``wheezy-backports`` repository on Debian
  Wheezy, newer version provides useful features. [drybjed]

- Update list of distributions after Jessie release as Stable. [drybjed]

v0.1.1
------

*Released: 2015-04-19*

- Fix a bug which caused iPXE to exit after a timeout back to the main menu
  without the timeout which could cause hosts to not boot at all. [drybjed]

v0.1.0
------

*Released: 2015-04-18*

- First release [drybjed]

