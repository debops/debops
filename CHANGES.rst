Changelog
=========

v0.1.1
------

*Released: 2015-05-01*

- Add ``resolvconf`` to list of packages installed by default. Debian Installer
  installs ``rdnssd`` if IPv6 network is detected which overrides
  ``/etc/resolv.conf`` if the former package is not installed. Adding
  ``resolvconf`` prevents loss of configuration like IPv4 nameservers and
  domain/search options. [drybjed]

- Add ``grub-installer`` Jinja block in the preseed templates. The destructive
  template will automatically install ``grub`` on a default partition on new
  Jessie installs. [drybjed]

- Switch from using one admin group to adding the admin account to multiple
  system groups, which will be created if necessary. [drybjed]

- Allow configuration of a system group which will be configured with
  passwordless ``sudo`` access. By default it will be first group defined in
  ``preseed_admin_groups`` list. [drybjed]

v0.1.0
------

*Released: 2015-04-12*

- Initial release [drybjed]

