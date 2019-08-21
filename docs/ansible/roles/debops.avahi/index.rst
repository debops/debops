.. _debops.avahi:

debops.avahi
============

`Avahi`__ is a Linux daemon which can be used to publish information about
local or remote services using `Multicast DNS`__ protocol (mDNS, also used by
Bonjour or ZeroConf). This protocol can then be queried by other applications
such as DNS clients or those that support `DNS Service Discovery`__ to find
out and access services on the local network.

.. __: https://www.avahi.org/
.. __: https://en.wikipedia.org/wiki/Multicast_DNS
.. __: https://en.wikipedia.org/wiki/Zero-configuration_networking#Service_discovery

The ``debops.avahi`` Ansible role can be used to configure the Avahi service on
Debian or Ubuntu hosts. You can create custom services, publish static host
entries that point to other hosts on the local network, or even define and
publish CNAME records pointing to the host itself via a custom script.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.avahi/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
