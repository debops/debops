Introduction
============

``debops.dhcpd`` role can be used to configure an `ISC DHCP Server`_ as
standalone or in a 2-host failover configuration. Alternatively, you can
configure an DHCP relay on a host connected to multiple networks which will
relay DHCP/BOOTP messages to your DHCP server.

``dhcp-probe`` script will be used to scan the network for unauthorized DHCP
servers and notify administrators if they are found.

.. _ISC DHCP Server: https://www.isc.org/downloads/dhcp/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
