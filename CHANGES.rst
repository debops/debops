Changelog
=========

v0.1.1
------

*Unreleased*

- Add ``resolvconf`` to list of packages installed by default. Debian Installer
  installs ``rdnssd`` if IPv6 network is detected which overrides
  ``/etc/resolv.conf`` if the former package is not installed. Adding
  ``resolvconf`` prevents loss of configuration like IPv4 nameservers and
  domain/search options. [drybjed]

- Add ``grub-installer`` Jinja block in the preseed templates. The destructive
  template will automatically install ``grub`` on a default partition on new
  Jessie installs. [drybjed]

v0.1.0
------

*Released: 2015-04-12*

- Initial release [drybjed]

