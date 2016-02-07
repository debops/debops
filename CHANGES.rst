Changelog
=========

v0.1.0
------

*Released: 2016-02-07*

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

- Remove hard role dependencies on ``ferm``, ``tcpwrappers`` and APT
  preferences. Move their configuration to default variables, which can be used
  from an Ansible playbook. [drybjed]

- Add support for ``/proc`` ``hidepid`` option. Role will detect it using
  Ansible local facts provided by the ``debops.console`` role and add ``snmp``
  user to the required system group. [drybjed]

- Make sure that variables which define SNMP passwords are set on all hosts
  during Ansible playbook run, since the old issue has been resolved. [drybjed]

