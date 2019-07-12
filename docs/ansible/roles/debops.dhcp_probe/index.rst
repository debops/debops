.. _debops.dhcp_probe:

debops.dhcp_probe
=================

The `dhcp_probe <https://www.net.princeton.edu/software/dhcp_probe/>`__ tool
can be used to passively detect rogue DHCP servers on IPv4 networks. Upon
detection, the service can execute custom commands to, for example, block the
culprit via RADIUS or notify the system administrator.

The ``debops.dhcp_probe`` role can be used to install and configure
:command:`dhcp_probe` on a Debian/Ubuntu host. It will utilize
:command:`systemd` instance templates to run DHCP Probe instances on multiple
network interfaces at once. By default, an e-mail message will be sent to the
system administrator with notification on newly detected rogue DHCP servers.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.dhcp_probe/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
