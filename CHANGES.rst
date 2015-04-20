Changelog
=========

v0.1.1
------

*Unreleased*

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

v0.1.0
------

*Released: 2015-04-20*

- First release, add Changelog. [drybjed]

