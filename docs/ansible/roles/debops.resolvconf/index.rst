.. _debops.resolvconf:

debops.resolvconf
=================

The :file:`/etc/resolv.conf` configuration file defines the system-wide DNS
resolver configuration. It is a central location to configure the DNS
nameservers, search domains and other options. In modern Linux systems, many
services might want to change that configuration file to enable their
functionality - `NetworkManager`__, ``ifupdown``, `dnsmasq`__, ``unbound``
being several examples of that.

.. __: https://wiki.debian.org/NetworkManager
.. __: https://wiki.debian.org/HowTo/dnsmasq

To avoid clashes between various software packages modifying the
:file:`/etc/resolv.conf` file, the ``resolvconf`` package provides a stable API
to the :file:`/etc/resolv.conf` that combines information from other services
and creates a consistent resolver configuration.

The ``debops.resolvconf`` Ansible role further updates the ``resolvconf``
configuration to fix issues with outdated defaults on modern Debian/Ubuntu
hosts. By default the role will update the interface order list to include the
`Predictable Network Interface Names`__ as well as clarify the order of the
NetworkManager interfaces. The role will also automatically rearrange the
configuration of VPN tunnels if a local DNS resolver is detected.

.. __: https://www.freedesktop.org/wiki/Software/systemd/PredictableNetworkInterfaceNames/

Contrary to its name, the ``debops.resolvconf`` role does not configure the
:file:`/etc/resolv.conf` file directly. You should consult the documentation of
various DNS-related services to see how you can modify the contents of this
file through them.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.resolvconf/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
