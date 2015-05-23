Changelog
=========

v0.1.2
------

*Unreleased*

- Check first argument in the delayed ifup script, if it's ``false``, specified
  interface won't be brought up at all. [drybjed]

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

