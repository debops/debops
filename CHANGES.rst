Changelog
=========

v0.1.1
------

*Released: 2015-10-15*

- Make sure that files specified in ``dhcpd_includes`` list exist before the
  DHCP server is restarted. [drybjed]

- Correctly handle IPv4 subnets with only 1 host inside. Previously they were
  parsed with errors, now ``debops.dhcpd`` will detect them hand handle
  separately from normal networks. [drybjed]

- Add support for iPXE boot loader chain-loading and DHCP options. [drybjed]

- Fix a templating error when IPv6 networking is not present on a host.
  [drybjed]

- Change the way role gathers the list of nameservers to avoid issue with
  ``sed`` command in shell module. [drybjed]

- Provide empty list of relay servers if default IPv4 gateway is not defined.
  [drybjed]

v0.1.0
------

*Released: 2015-03-30*

- First release [drybjed]

