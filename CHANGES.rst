Changelog
=========

v0.1.0
------

*Unreleased*

- Initial release. [drybjed]

- Fix wrongly named variable in ``/etc/default/snmpd``. [drybjed]

- Install a custom ``snmpd.service`` unit file to replace Debian provided init
  script, which causes issues with ``snmpd`` daemon on hosts with LXC
  containers. This unit file will be automatically activated on hosts with
  ``systemd`` enabled. [drybjed]

- Ignore "link-local" IPv6 addresses in list of IP addresses / subnets allowed
  to connect to ``snmpd``. [drybjed]

- Fix wrong permissions in ``/etc/default/{lldpd,snmpd}`` configuration files.
  [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

- Reload ``systemd`` daemons when a replacement ``snmpd.service`` unit is
  installed and enable it "manually" because the Ansible ``service`` module
  doesn't want to play nice with both ``systemd`` unit and ``sysvinit`` script
  being present. [drybjed]

