Changelog
=========

v0.2.5
------

*Unreleased*

- Fix an issue with ``systemd`` ``network-online.target`` on Debian where it
  starts at the same time as ``network.target``, and doesn't wait for
  ``ifupdown`` scripts to finish network configuration. More details:
  https://unix.stackexchange.com/q/209832 [drybjed]

- Fixed Ansible check mode related to the ``ifup-wait-all-auto`` ``systemd``
  service might not being defined. [ypid]

v0.2.4
------

*Released: 2016-02-11*

- Fix deprecation warnings on Ansible 2.1.0. [drybjed]

- The ``item.delete`` parameter will be now tested as a boolean. [drybjed]

- Rename the ``ifupdown`` variable to ``ifupdown_enabled`` and move the POSIX
  capability detection to default variables. You might need to update inventory
  if you disabled ``debops.ifupdown`` role. [drybjed]

v0.2.3
------

*Released: 2015-11-24*

- Fix issues during Ansible ``--check`` mode, role should no longer stop due to
  not existing dictionary keys. [drybjed]

- Fix an issue where Jinja templating of the ``ifupdown`` variable resulted in
  a new line character added in Ansible v2. [drybjed]

- Ignore comment lines while checking if static network configuration is
  present. [drybjed]

- Updated documentation and fixed spelling. [ypid]

- Add ``ifupdown_interface_weight_map`` variable.

  This variable defines default values of ``item.weight`` parameter for
  different interface types. This is needed because order of interfaces managed
  by ``ifupdown`` is significant and different interface types should be
  specified in correct order (for example interface definitions should be
  specified before bridges that use these interfaces).

  If you specify the weight of each interface manually using ``item.weight``
  parameter, your configuration shouldn't be affected.

  This change will most likely generate new sets of interface configuration in
  ``/etc/network/interfaces.d/`` on already configured hosts. To prevent
  duplication of configuration, you can remove the configuration stored in
  ``/etc/network/interfaces.config.d/`` before running the role.

  Because from the ``ifupdown`` perspective configuration of each interface
  changed, after new configuration is generated each interface will be brought
  down and up again. You shouldn't lose the connection to remote host, but
  local (or remote console) access might be handy.

  Because bridges will be restarted, any external interfaces connected to them
  will be dropped. That means that virtual machines and containers will lose
  the network connection permanently. Restarting the afftected virtual machines
  and containers should bring everything back to normal. [drybjed]

- Add a way to set custom comments for each interface using dictionary maps.
  [drybjed]

- Add a way to prevent modification of live interfaces.

  By setting ``ifupdown_reconfigure_auto`` variable to ``False`` you can
  prevent the role from messing with the live network configuration, but still
  configure the interfaces in ``/etc/network/interfaces``. This is useful on
  a production server with virtual machines or containers running, since it
  prevents modification to network bridges which requires restart of the
  network interfaces and may drop the existing bridge layout. [drybjed]

v0.2.2
------

*Released: 2015-08-08*

- Streamline directory creation tasks and make sure required packages are
  installed. [le9i0nx]

- Make sure that Ansible does not stop if a variable is undefined. This change
  fixes issues with the missing variables in Ansible v2. [drybjed]

v0.2.1
------

*Released: 2015-06-01*

- Add a text block variable with options for bridge interfaces which becomes
  active when user does not specify any options for that bridge. By default
  these options will set forward delay to ``0`` to make DHCP queries work
  correctly on virtual machine boot. [drybjed]

v0.2.0
------

*Released: 2015-05-30*

- Expose path to reconfiguration script in a default variable, so that it can
  be changed if needed. [drybjed]

- Add variable with list of APT packages to install and automatically install
  certain packages depending on what interface types are present in the
  configuration. [drybjed]

- Add an option to ignore "static" configuration in
  ``/etc/network/interfaces``. [drybjed]

- Change reconfiguration script ``logger`` command to not cut the emitted
  string after first variable. And it looks cleaner now. [drybjed]

- Interface configuration overhaul.

  Most changes are related to configuration templates. Instead of having
  duplicate configuration in each of the templates, most of the configuration
  is now in ``interface.j2`` template; other templates extend this one.

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
  a separate commit. [drybjed]

v0.1.2
------

*Released: 2015-05-24*

- Check first argument in the delayed ifup script, if it's ``false``, specified
  interface won't be brought up at all. [drybjed]

- Remove management if ``ifup@.service`` unit symlinks for configured
  interfaces. ``ifupdown`` and ``/etc/init.d/networking`` scripts work just
  fine without them present. [drybjed]

- Split ``interface_enabled`` list into two to better track what types of
  interfaces are enabled. Additionally, send list of configured interfaces to
  the syslog for debugging purposes. [drybjed]

- Add ``item.port_active`` parameter to bridge configuration.

  If this parameter is set, specified ``item.port`` or ``item.port_present``
  must be in a given active state (``True`` / ``False``) to configure the
  bridge.

  This helps mitigate an issue where bridge with DHCP configuration is
  constantly running ``dhclient`` when its main interface is not connected to
  the network. [drybjed]

- Add a way to postpone interface configuration entirely using a separate
  temporary script, with optional pre- and post- commands. This script will be
  run at the end of the current play, or can be executed independently.
  [drybjed]

v0.1.1
------

*Released: 2015-05-12*

- Add ``item.port_present`` parameter in bridge configuration. It can be used
  to enable or disable specific bridge interface depending on presence of
  a given network interface in ``ansible_interfaces`` list, but does not affect
  the configuration of the bridge itself. [drybjed]

- Clean up ``allow-auto`` and ``allow-hotplug`` options in interface
  configuration. By default both of these parameters will be added
  automatically by ``debops.ifupdown`` to most of the interface types unless
  specifically disabled.

  This tells the system to start the interfaces at boot time, as well as allows
  to control specific interfaces by the hotplug events using ``ifup`` and
  ``ifdown`` commands or ``ifup@.service`` under ``systemd``. [drybjed]

- Add IPv6 SLAAC configuration on all default interfaces; this is required on
  Debian Jessie to enable IPv6 address autoconfiguration.  [drybjed]

- Rewrite network interface configuration logic.

  Generate interface configuration in a separate
  ``/etc/network/interfaces.config.d/`` directory instead of directly in
  ``/etc/network/interfaces.d/`` directory. Provide original configuration at
  first run of the role, which is required to properly shut down all network
  interfaces, when state of the networking configuration is undefined.

  Instead of disabling and enabling network interfaces directly using Ansible
  tasks and ``ifup`` / ``ifdown`` commands, delegate the reconfiguration
  process to an external script installed on the host. The script will properly
  disable and enable interfaces in systems using sysvinit, upstart and systemd.

  The ifupdown configuration script will shut down all network interfaces on
  the first run of the ``debops.ifupdown`` role, apply configuration changes
  from the ``/etc/network/interfaces.config.d/`` directory to
  ``/etc/network/interfaces.d/`` directory and then start only enabled
  interfaces using ``ifup`` command or ``ifup@.service`` systemd service. Only
  network interfaces which have been modified will be enabled/disabled on
  subsequent runs. [drybjed]

- Add a way to delay activation of specific network interface.

  A network interface can be prepared beforehand by ``debops.ifupdown`` role,
  then additional configuration can be performed (for example an OpenVPN/tinc
  VPN, GRE tunnel, etc.) and after that the other role can run the script
  prepared by ``debops.ifupdown`` in a known location to start the interface.

  This option is enabled by adding ``item.auto_ifup: False`` to interface
  configuration. [drybjed]

v0.1.0
------

*Released: 2015-04-20*

- First release, add Changelog. [drybjed]

