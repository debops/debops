Enhancements to ifupdown in systemd
===================================

.. contents::
   :local:

ifup-all-auto.service
---------------------

This :command:`systemd` unit should make sure that all of the network interfaces that
are enabled by ``allow-auto`` parameter are up before the
:file:`network-online.target` is reached. This makes that target usable on
Debian/Ubuntu hosts; services that depend on that target should work properly
with the assumption that the host has network connectivity at that point.


ifup-allow-boot.service
-----------------------

This :command:`systemd` unit will bring up all network interfaces that are
marked by ``allow-boot`` and ``allow-hotplug`` parameters at system boot time.
It is run after the :file:`networking.service` unit and will use the command
:command:`systemctl start ifup@<interface>.service` to start the interfaces, so
that any processes that are attached to them will be put in their separate
cgroups. This allows better network management on :command:`systemd` hosts.
