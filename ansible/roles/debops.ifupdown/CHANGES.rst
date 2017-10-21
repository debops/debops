.. _ifupdown__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.ifupdown**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.ifupdown master`_ - unreleased
--------------------------------------

.. _debops.ifupdown master: https://github.com/debops/ansible-ifupdown/compare/v0.4.0...master


`debops.ifupdown v0.4.0`_ - 2017-07-12
--------------------------------------

.. _debops.ifupdown v0.4.0: https://github.com/debops/ansible-ifupdown/compare/v0.3.2...v0.4.0

Added
~~~~~

- Add a separate ``iface@.service`` :command:`systemd` unit file which is used
  to setup network interfaces that don't have an explicit device related to
  them (bridges, VLAN interfaces, bonding interfaces).

  This is required because of the recent changes in the ``ifupdown`` package in
  Debian Jessie/Stretch which change the ``ifup@.service`` unit file to have
  the related device of a given interface as a dependency. As a result, the
  ``ifup@.service`` instances that don't have an explicit device associated
  with them (anything other than a physical Ethernet network interface) wait
  endlessly for a device that it's not present. This doesn't happen if the
  network interfaces are configured using :command:`systemd-networkd`
  facilities, but because this role provides a pure ``ifupdown``
  implementation, this was the easiest way to solve that issue. [drybjed_]

- Add support for the ``weight_class`` interface parameter which allows to
  affect filename sorting. [drybjed_]

- Add proper :command:`iptables` firewall rules to handle broadcast and
  multicast traffic on local IPv4 network behind NAT and not masquerade or
  forward it. This is needed for mDNS/Avahi support. [drybjed_]

Changed
~~~~~~~

- Change the weight numbers from 2 to 3 digits. This might affect network
  configuration during the transition phase if the network interfaces are
  configured by other roles than just internally by the ``debops.ifupdown``
  role. [drybjed_]

- The autoconfiguration of the VLAN network interfaces is changed to create
  better interface order. The role will check what interface type the VLAN
  interface is attached to and the VLAN interface will use the weight of the
  parent interface to ensure that the VLAN interface is configured after the
  parent interface. [drybjed_]

- Improve Jinja templates by removing redundancy. [ypid_]

- Role now requires at least Ansible v2.2 due to use of the ``check_mode:
  False`` directive. [drybjed_]


`debops.ifupdown v0.3.2`_ - 2016-12-16
--------------------------------------

.. _debops.ifupdown v0.3.2: https://github.com/debops/ansible-ifupdown/compare/v0.3.1...v0.3.2

Fixed
~~~~~

- Fix an "unbound variable" issue in the ``ifupdown-reconfigure-interfaces``
  script on Debian Jessie systems without :command:`systemd` init. [drybjed_]


`debops.ifupdown v0.3.1`_ - 2016-11-25
--------------------------------------

.. _debops.ifupdown v0.3.1: https://github.com/debops/ansible-ifupdown/compare/v0.3.0...v0.3.1

Changed
~~~~~~~

- Update the ``merge_dict`` Jinja macro to a more general version which
  supports both YAML dictionaries and YAML lists. [drybjed_]

- Change the Ethernet interface detection so that Ansible checks if the
  interface has an associated kernel module. This should prevent the role from
  detecting VPN tunnels as Ethernet interfaces. [drybjed_]


`debops.ifupdown v0.3.0`_ - 2016-11-17
--------------------------------------

.. _debops.ifupdown v0.3.0: https://github.com/debops/ansible-ifupdown/compare/v0.2.6...v0.3.0

Added
~~~~~

- Add the :file:`ifup-allow-boot.service` :command:`systemd` unit file which
  will bring up all network interfaces which have the ``allow-boot`` and
  ``allow-hotplug`` parameters. This should fix a problem where network
  interfaces that don't use hotplug events (like bridges, tunnels, etc.) are
  not brought up by the :file:`networking.service` unit, or are brought up with
  their processes put in the :file:`networking.service` cgroup and not able to
  be managed separately. [drybjed_]

- Role will now mark the network interfaces that need processing (new, removed,
  or changed) using files in the :file:`/run/network/` directory. The network
  reconfiguration script reads these files and performs network changes if
  needed. [drybjed_]

- The ``debops.ifupdown`` role now incorporates configuration done by the
  ``debops.subnetwork`` role; it generates the forward and NAT rules for the
  firewall managed by the debops.ferm_ Ansible role for each bridge it manages.
  This is configurable per bridge if needed. [drybjed_]

- Role now uses separate ``debops.ifupdown/env`` internal role to prepare
  dynamic configuration for other roles, like debops.ferm_. You will need to
  update your playbooks to reflect this. [drybjed_]

- You can now install custom scripts or other files needed by the interface
  configuration by using the new :envvar:`ifupdown__custom_files` variables.
  [drybjed_]

- Role now supports the stable network interface naming schemes introduced by
  the :command:`systemd` init daemon. The network interfaces should be
  correctly detected without the need for the user to configure them beforehand
  using role variables. [drybjed_]

- You can now use variables on different inventory levels to configure network
  interfaces on all or specific groups of hosts. [drybjed_]

- Role now uses Ansible local fact script to preserve some configuration like
  information about external and internal network interfaces to make the role
  operation idempotent. [drybjed_]

- Save information about role version in a central location managed by
  debops.debops_fact_ Ansible role. [drybjed_]

- Use information about deployed role version to reset the network
  configuration if necessary to avoid issues with duplicated network
  interfaces. [drybjed_]

- Add an option to disable automatic reconfiguration of the network interfaces.
  The reconfiguration script will be installed on the remote host and will
  allow to control reconfiguration manually. [drybjed_]

- Add interface layout ``manual`` to not use any network interface layout and
  allow you to configure interfaces manually. [ypid_]

- Allow flexible and advanced Firewall configuration using
  ``forward_interface_ferm_rule`` and ``forward_outerface_ferm_rule`` and added
  a example for it.
  ``debops.subnetwork`` supported similar configuration using the
  ``subnetwork__allow_*`` variables. [ypid_]

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]

- Rename all role variables from ``ifupdown_*`` to ``ifupdown__*`` to put them
  in a separate namespace. You will need to update your Ansible inventory. Keep
  in mind that the variable data model has also been changed, read the rest of
  the documentation for details. [drybjed_]

- Change the network interface configuration model from YAML list to a YAML
  dict. This should make the role less prone to creating duplicate interface
  configuration. [drybjed_]

- Configuration file naming scheme in :file:`/etc/network/interfaces.d/` has
  been simplified to eliminate issues with duplicating network interface
  configuration. Now all files are named as ``<weight>_iface_<interface>``;
  IPv4 and IPv6 interface configuration is stored in 1 file instead of 2.
  [drybjed_]

- The ``debops.ifupdown`` role will ensure that the :command:`rdnssd` package
  is installed for better IPv6 DNS support. [drybjed_]

- The default network configuration layouts have been moved to the default role
  variables and can be easily changed or extended if necessary. [drybjed_]

- All of the network interface configuration has been merged into 1 YAML
  dictionary, there's no need to configure separate parameters in separate
  "maps" anymore. [drybjed_]

- The interface reconfiguration script now sends information about different
  operations to :command:`syslog` for easier debugging. [drybjed_]

- Network interfaces that require changes are reconfigured in reverse order to
  behave the same as the :command:`ifupdown` commands. [drybjed_]

- Rename the ``dhcp`` interface layout to ``dynamic``. [drybjed_]

- Redesign th ``gateway`` parameter to work similar to ``address`` parameter.
  [drybjed_]

- Make the ``weight`` parameter a bit more useful by adding it to the base
  weight defined by the interface type instead of setting the weight directly.
  This makes interface order easier to define without the need to look up the
  specific weight. [drybjed_]

- Remove the interface configuration files that have wrong weight in their
  filename to make interface reordering easier. [drybjed_]

Deprecated
~~~~~~~~~~

- The ``debops.subnetwork`` Ansible role has been deprecated by this role and
  shouldn't be used anymore. [drybjed_]

Removed
~~~~~~~

- Remove all files in :file:`var/` directory; the default interface
  configuration is moved to the :envvar:`ifupdown__default_interfaces` variable.
  [drybjed_]

- Drop usage of locally installed reconfiguration script, it's now used by the
  :file:`script` Ansible module directly. [drybjed_]

- Remove environment detection code, that is detection of POSIX capabilities,
  detection of static network configuration in :file:`/etc/network/interfaces`
  and detection of NetworkManager service. The role is no longer included in
  the DebOps :file:`common.yml` playbook, therefore it assumes that it can
  operate correctly on all hosts where it's enabled and those checks shouldn't
  be needed. [drybjed_]

- Remove support for ``dns_nameservers{4,6}`` and ``dns_search{4,6}`` from the
  interface configuration, the normal parameters ``dns_nameservers`` and
  ``dns_search`` are enough to support this functionality. [drybjed_]

Fixed
~~~~~

- Fix bug that caused the role to abort when a host has interface names with a
  hyphen configured. [ypid_]

- Don’t fail if ``ansible_default_ipv4`` is an empty dictionary. [ypid_]

- Don’t fail if a host does not have DNS nameservers defined
  (``ansible_dns.nameservers`` is undefined). [ypid_]

- Don’t fail if a host does not have a DNS search domain specified
  (``ansible_dns.search`` is undefined). [ypid_]

`debops.ifupdown v0.2.6`_ - 2016-10-20
--------------------------------------

.. _debops.ifupdown v0.2.6: https://github.com/debops/ansible-ifupdown/compare/v0.2.5...v0.2.6

Changed
~~~~~~~

- Make sure that role passes correctly even if ``ifupdown_capabilities`` was
  not set. [drybjed_]


`debops.ifupdown v0.2.5`_ - 2016-07-17
--------------------------------------

.. _debops.ifupdown v0.2.5: https://github.com/debops/ansible-ifupdown/compare/v0.2.4...v0.2.5

Changed
~~~~~~~

- Use relative paths with ``with_first_found`` lookup. [drybjed_]

Fixed
~~~~~

- Fix an issue with ``systemd`` ``network-online.target`` on Debian where it
  starts at the same time as ``network.target``, and doesn't wait for
  ``ifupdown`` scripts to finish network configuration. More details:
  https://unix.stackexchange.com/q/209832 [drybjed_]

- Fixed Ansible check mode related to the ``ifup-wait-all-auto`` ``systemd``
  service might not being defined. [ypid_]


`debops.ifupdown v0.2.4`_ - 2016-02-11
--------------------------------------

.. _debops.ifupdown v0.2.4: https://github.com/debops/ansible-ifupdown/compare/v0.2.3...v0.2.4

Changed
~~~~~~~

- The ``item.delete`` parameter will be now tested as a boolean. [drybjed_]

- Rename the ``ifupdown`` variable to ``ifupdown_enabled`` and move the POSIX
  capability detection to default variables. You might need to update inventory
  if you disabled ``debops.ifupdown`` role. [drybjed_]

Fixed
~~~~~

- Fix deprecation warnings on Ansible 2.1.0. [drybjed_]


`debops.ifupdown v0.2.3`_ - 2015-11-24
--------------------------------------

.. _debops.ifupdown v0.2.3: https://github.com/debops/ansible-ifupdown/compare/v0.2.2...v0.2.3

Added
~~~~~

- Add ``ifupdown_interface_weight_map`` variable.

  This variable defines default values of ``item.weight`` parameter for
  different interface types. This is needed because order of interfaces managed
  by ``ifupdown`` is significant and different interface types should be
  specified in correct order (for example interface definitions should be
  specified before bridges that use these interfaces).

  If you specify the weight of each interface manually using ``item.weight``
  parameter, your configuration shouldn't be affected.

  This change will most likely generate new sets of interface configuration in
  :file:`/etc/network/interfaces.d/` on already configured hosts. To prevent
  duplication of configuration, you can remove the configuration stored in
  :file:`/etc/network/interfaces.config.d/` before running the role.

  Because from the ``ifupdown`` perspective configuration of each interface
  changed, after new configuration is generated each interface will be brought
  down and up again. You shouldn't lose the connection to remote host, but
  local (or remote console) access might be handy.

  Because bridges will be restarted, any external interfaces connected to them
  will be dropped. That means that virtual machines and containers will lose
  the network connection permanently. Restarting the affected virtual machines
  and containers should bring everything back to normal. [drybjed_]

- Add a way to set custom comments for each interface using dictionary maps.
  [drybjed_]

- Add a way to prevent modification of live interfaces.

  By setting ``ifupdown_reconfigure_auto`` variable to ``False`` you can
  prevent the role from messing with the live network configuration, but still
  configure the interfaces in :file:`/etc/network/interfaces`. This is useful on
  a production server with virtual machines or containers running, since it
  prevents modification to network bridges which requires restart of the
  network interfaces and may drop the existing bridge layout. [drybjed_]

Changed
~~~~~~~

- Ignore comment lines while checking if static network configuration is
  present. [drybjed_]

- Updated documentation and fixed spelling. [ypid_]

Fixed
~~~~~

- Fix issues during Ansible ``--check`` mode, role should no longer stop due to
  not existing dictionary keys. [drybjed_]

- Fix an issue where Jinja templating of the ``ifupdown`` variable resulted in
  a new line character added in Ansible v2. [drybjed_]


`debops.ifupdown v0.2.2`_ - 2015-08-08
--------------------------------------

.. _debops.ifupdown v0.2.2: https://github.com/debops/ansible-ifupdown/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Streamline directory creation tasks and make sure required packages are
  installed. [le9i0nx_]

- Make sure that Ansible does not stop if a variable is undefined. This change
  fixes issues with the missing variables in Ansible v2. [drybjed_]


`debops.ifupdown v0.2.1`_ - 2015-06-01
--------------------------------------

.. _debops.ifupdown v0.2.1: https://github.com/debops/ansible-ifupdown/compare/v0.2.0...v0.2.1

Added
~~~~~

- Add a text block variable with options for bridge interfaces which becomes
  active when user does not specify any options for that bridge. By default
  these options will set forward delay to ``0`` to make DHCP queries work
  correctly on virtual machine boot. [drybjed_]


`debops.ifupdown v0.2.0`_ - 2015-05-30
--------------------------------------

.. _debops.ifupdown v0.2.0: https://github.com/debops/ansible-ifupdown/compare/v0.1.2...v0.2.0

Added
~~~~~

- Expose path to reconfiguration script in a default variable, so that it can
  be changed if needed. [drybjed_]

- Add variable with list of APT packages to install and automatically install
  certain packages depending on what interface types are present in the
  configuration. [drybjed_]

- Add an option to ignore "static" configuration in
  :file:`/etc/network/interfaces`. [drybjed_]

Changed
~~~~~~~

- Change reconfiguration script ``logger`` command to not cut the emitted
  string after first variable. And it looks cleaner now. [drybjed_]

- Interface configuration overhaul.

  Most changes are related to configuration templates. Instead of having
  duplicate configuration in each of the templates, most of the configuration
  is now in :file:`interface.j2` template; other templates extend this one.

  ``item.aliases`` list has been removed. Instead, there's now new parameter,
  ``item.addresses``. This is a list of IP addresses in the ``host/prefix``
  notation which should be set on a given interface. You can specify multiple
  IPv4 or IPv6 addresses this way, and role will generate correct configuration
  depending on if the interface is set in ``dhcp`` or ``static`` mode.

  You can "augment" current interface configuration using separate dict
  variables in Ansible inventory, in the format
  ``ifupdown_map_<type>_<variable>``, each dict should have an interface name
  as the key and list or string of parameters you want to add/change. For
  example, to add additional IP addresses to an interface using inventory, you
  can specify them as::

      ifudpdown_map_interface_addresses:
        'br0': [ '192.0.2.0/24', '2001:db8:dead:beef::1/64' ]

  List of possible dict variables will be added in the documentation in
  a separate commit. [drybjed_]


`debops.ifupdown v0.1.2`_ - 2015-05-24
--------------------------------------

.. _debops.ifupdown v0.1.2: https://github.com/debops/ansible-ifupdown/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add ``item.port_active`` parameter to bridge configuration.

  If this parameter is set, specified ``item.port`` or ``item.port_present``
  must be in a given active state (``True`` / ``False``) to configure the
  bridge.

  This helps mitigate an issue where bridge with DHCP configuration is
  constantly running :program:`dhclient` when its main interface is not connected to
  the network. [drybjed_]

- Add a way to postpone interface configuration entirely using a separate
  temporary script, with optional pre- and post- commands. This script will be
  run at the end of the current play, or can be executed independently.
  [drybjed_]

Changed
~~~~~~~

- Check first argument in the delayed ifup script, if it's ``false``, specified
  interface won't be brought up at all. [drybjed_]

- Split ``interface_enabled`` list into two to better track what types of
  interfaces are enabled. Additionally, send list of configured interfaces to
  the syslog for debugging purposes. [drybjed_]

Removed
~~~~~~~

- Remove management if ``ifup@.service`` unit symlinks for configured
  interfaces. ``ifupdown`` and :file:`/etc/init.d/networking` scripts work just
  fine without them present. [drybjed_]


`debops.ifupdown v0.1.1`_ - 2015-05-12
--------------------------------------

.. _debops.ifupdown v0.1.1: https://github.com/debops/ansible-ifupdown/compare/v0.1.0...v0.1.1

Added
~~~~~

- Add ``item.port_present`` parameter in bridge configuration. It can be used
  to enable or disable specific bridge interface depending on presence of
  a given network interface in ``ansible_interfaces`` list, but does not affect
  the configuration of the bridge itself. [drybjed_]

- Add IPv6 SLAAC configuration on all default interfaces; this is required on
  Debian Jessie to enable IPv6 address autoconfiguration.  [drybjed_]

- Add a way to delay activation of specific network interface.

  A network interface can be prepared beforehand by ``debops.ifupdown`` role,
  then additional configuration can be performed (for example an OpenVPN/tinc
  VPN, GRE tunnel, etc.) and after that the other role can run the script
  prepared by ``debops.ifupdown`` in a known location to start the interface.

  This option is enabled by adding ``item.auto_ifup: False`` to interface
  configuration. [drybjed_]

Changed
~~~~~~~

- Clean up ``allow-auto`` and ``allow-hotplug`` options in interface
  configuration. By default both of these parameters will be added
  automatically by ``debops.ifupdown`` to most of the interface types unless
  specifically disabled.

  This tells the system to start the interfaces at boot time, as well as allows
  to control specific interfaces by the hotplug events using ``ifup`` and
  ``ifdown`` commands or ``ifup@.service`` under ``systemd``. [drybjed_]

- Rewrite network interface configuration logic.

  Generate interface configuration in a separate
  :file:`/etc/network/interfaces.config.d/` directory instead of directly in
  :file:`/etc/network/interfaces.d/` directory. Provide original configuration at
  first run of the role, which is required to properly shut down all network
  interfaces, when state of the networking configuration is undefined.

  Instead of disabling and enabling network interfaces directly using Ansible
  tasks and ``ifup`` / ``ifdown`` commands, delegate the reconfiguration
  process to an external script installed on the host. The script will properly
  disable and enable interfaces in systems using sysvinit, upstart and systemd.

  The ifupdown configuration script will shut down all network interfaces on
  the first run of the ``debops.ifupdown`` role, apply configuration changes
  from the :file:`/etc/network/interfaces.config.d/` directory to
  :file:`/etc/network/interfaces.d/` directory and then start only enabled
  interfaces using ``ifup`` command or ``ifup@.service`` systemd service. Only
  network interfaces which have been modified will be enabled/disabled on
  subsequent runs. [drybjed_]


debops.ifupdown v0.1.0 - 2015-04-20
-----------------------------------

Added
~~~~~

- First release, add Changelog. [drybjed_]
