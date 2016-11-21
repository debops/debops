.. _tinc__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.tinc**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.

Refer to the :ref:`tinc__ref_upgrade_nodes` when you intend to upgrade to a
new release.


`debops.tinc master`_ - unreleased
----------------------------------

.. _debops.tinc master: https://github.com/debops/ansible-tinc/compare/v0.3.0...master


`debops.tinc v0.3.0`_ - 2016-11-21
----------------------------------

.. _debops.tinc v0.3.0: https://github.com/debops/ansible-tinc/compare/v0.2.1...v0.3.0

Added
~~~~~

- Add :envvar:`tinc__address_family_mesh0` and :envvar:`tinc__compression_mesh0`. [ser_]

- Add :envvar:`tinc__mlock_mesh0`. [ypid_]

- Allow to configure nodes as clients using :envvar:`tinc__client_hosts`. [ypid_]

- Add support to block default route and DNS servers offered via DHCPv4 over a
  Tinc network. Tinc nodes will not accept default routes thought the mesh
  network anymore. Furthermore allow to adjust the metric of routes created
  based on those offered via DHCPv4. [ypid_]

- Ensure that highly sensitive files are not checked into version control when
  for example :program:`etckeeper` is used for tracking changes in :file:`/etc`.
  Note that sensitive files which are already tracked by version control will
  need to be manually deleted from version control history!
  Refer to :envvar:`tinc__vcs_ignore_patterns` for more details. [ypid_]

Changed
~~~~~~~

- Update to DebOps Standards v0.2.1. [ypid_]

- Rename undocumented ``delete`` option for :ref:`tinc__ref_networks` to
  ``state`` and document it. [ypid_]

- :envvar:`tinc__inventory_hosts_mesh0` now refers to all hosts in the Ansible
  inventory that are participating in the ``mesh0`` network. [ypid_]

- Rename ``tinc__connect_to_mesh0`` to :envvar:`tinc__reachable_peer_hosts_mesh0`.
  [ypid_]

- Increased default RSA key size from ``4096`` to ``8192`` bits as suggested by
  https://bettercrypto.org. Note that this increases the initial key generation
  from a few seconds to a few minutes which should be justifiable. [ypid_]

- Update documentation to use debops.ifupdown_ instead of the
  deprecated ``debops.subnetwork`` role. [ypid_]

- Set the correct version in the upgrade notes and update the upgrade script
  name. [drybjed_]

Fixed
~~~~~

- Redundancy and deviation in documentation. [ypid_]

- Don’t connect to the Tinc daemon node itself when working with FQDNs. [ypid_]

- Don’t rely on the legacy :command:`brctl` command to be installed (which was not ensured by
  this role) and instead use tools from the ``iproute2`` package. [ypid_]


`debops.tinc v0.2.1`_ - 2016-02-29
----------------------------------

.. _debops.tinc v0.2.1: https://github.com/debops/ansible-tinc/compare/v0.2.0...v0.2.1

Added
~~~~~

- Add a way to exclude addresses from the public key host files. The default
  ``mesh0`` configuration will automatically gather all relevant IP addresses
  and exclude them from the host files. [drybjed_]

Changed
~~~~~~~

- Use the same value type in :envvar:`tinc__host_addresses_fqdn` and
  :envvar:`tinc__host_addresses_ip` for consistency. [drybjed_]

- Support both strings and lists in :envvar:`tinc__host_addresses`. [drybjed_]

- Use separate :envvar:`tinc__inventory_hostname` variable synchronized with the
  ``inventory_hostname`` variable to transfer files correctly between hosts.
  [drybjed_]

- Switch init service detection from debops.core_ Ansible local fact to
  internal ``ansible_service_mgr`` variable. This increases the role
  requirements to Ansible v2.0. [drybjed_]

- Use only the hostname in the ``ConnectTo`` list if a FQDN name is used in the
  inventory. [drybjed_]


`debops.tinc v0.2.0`_ - 2016-02-22
----------------------------------

.. _debops.tinc v0.2.0: https://github.com/debops/ansible-tinc/compare/v0.1.1...v0.2.0

Changed
~~~~~~~

- Rewrite of the ``debops.tinc`` role.

  The role now supports management of multiple Tinc VPNs at the same time. By
  default a ``mesh0`` network is established, which uses the Switch mode and
  DHCP to manage network configuration.

  The new role doesn't use ``ifupdown`` configuration to manage the network
  interfaces, instead custom ``tinc-up`` and ``tinc-down`` scripts take care of
  setting up and tearing down the virtual Ethernet interface used by the VPN.

  If ``systemd`` is detected on a host, the role installs custom service units
  that allow to manage each Tinc VPN separately from the others. The role uses
  these units as needed to start/stop/restart the daemons.

  Configuration for debops.etc_services_, debops.ferm_ and
  debops.secret_ Ansible roles is generated dynamically by custom templates.
  This requires a customized Ansible playbook (see the documentation).

  Public RSA host keys are not distributed using YAML text blocks. Instead,
  debops.secret_ role manages as set of directories which can be used to
  deploy public keys to the hosts in the mesh. [drybjed_]


`debops.tinc v0.1.1`_ - 2015-11-30
----------------------------------

.. _debops.tinc v0.1.1: https://github.com/debops/ansible-tinc/compare/v0.1.0...v0.1.1

Added
~~~~~

- New variable ``tinc_interface_auto`` which controls if VPN interface will be
  started at boot time, and if Ansible will automatically manage it during
  playbook runs if any changes occur. [drybjed_]

Changed
~~~~~~~

- Change the ``tinc_host_port`` type from Int to String, so that there are no
  issues with the debops.ferm_ role. [drybjed_]

- Wrap the name of the VPN node and replace all hyphens with underscores, which
  is a ``tinc`` requirement. [drybjed_]

Fixed
~~~~~

- Fix wrong name of the variable in host template. [drybjed_]


debops.tinc v0.1.0 - 2015-05-20
-------------------------------

Added
~~~~~

- Initial release. [drybjed_]
