Changelog
=========

v0.1.1
------

*Unreleased*

- Make sure that files specified in ``dhcpd_includes`` list exist before the
  DHCP server is restarted. [drybjed]

- Correctly handle IPv4 subnets with only 1 host inside. Previously they were
  parsed with errors, now ``debops.dhcpd`` will detect them hand handle
  separately from normal networks. [drybjed]

v0.1.0
------

*Released: 2015-03-30*

- First release [drybjed]

