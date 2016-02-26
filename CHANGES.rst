Changelog
=========

v0.2.1
------

*Released: 2016-02-26*

- Use the same value type in ``tinc__host_addresses_fqdn`` and
  ``tinc__host_addresses_ip`` for consistency. [drybjed]

- Support both strings and lists in ``tinc__host_addresses``. [drybjed]

- Use separate ``tinc__inventory_hostname`` variable synchronized with the
  ``inventory_hostname`` variable to transfer files correctly between hosts.
  [drybjed]

v0.2.0
------

*Released: 2016-02-22*

- Rewrite of the ``debops.tinc`` role.

  The role now supports management of multiple Tinc VPNs at the same time. By
  default a ``mesh0`` network is estabilished, which uses the Switch mode and
  DHCP to manage network configuration.

  The new role ddoesn't use ``ifupdown`` configuration to manage the network
  interfaces, instead custom ``tinc-up`` and ``tinc-down`` scripts take care of
  setting up and tearing down the virtual Ethernet interface used by the VPN.

  If ``systemd`` is detected on a host, role installs custom service units that
  allow to manage each Tinc VPN separately from the others. The role uses these
  units as needed to start/stop/restart the daemons.

  Configuration for ``debops.etc_services``, ``debops.ferm`` and
  ``debops.secret`` Ansible roles is generated dynamically by custom templates.
  This requires a customized Ansible playbook (see the documentation).

  Public RSA host keys are not distributed using YAML text blocks. Instead,
  ``debops.secret`` role manages as set of directories which can be used to
  deploy public keys to the hosts in the mesh. [drybjed]

v0.1.1
------

*Released: 2015-11-30*

- New variable ``tinc_interface_auto`` wich controls if VPN interface will be
  started at boot time, and if Ansible will automatically manage it during
  playbook runs if any changes occur. [drybjed]

- Change the ``tinc_host_port`` type from Int to String, so that there are no
  issues in ``debops.ferm`` role. [drybjed]

- Fix wrong name of the variable in host template. [drybjed]

- Wrap the name of the VPN node and replace all hypens with underscores, which
  is a ``tinc`` requirement. [drybjed]

v0.1.0
------

*Released: 2015-05-20*

- Initial release. [drybjed]

