.. _debops.dhcpd:

debops.dhcpd
============

``debops.dhcpd`` role can be used to configure an `ISC DHCP Server`_ as
standalone or in a 2-host failover configuration. Alternatively, you can
configure an DHCP relay on a host connected to multiple networks which will
relay DHCP/BOOTP messages to your DHCP server.

.. _ISC DHCP Server: https://www.isc.org/downloads/dhcp/

.. toctree::
   :maxdepth: 3

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/dhcpd/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
