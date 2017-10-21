Introduction
============

Avahi is a Linux daemon which can be used to publish information about local or
remote services using `Multicast DNS <https://en.wikipedia.org/wiki/Multicast_DNS>`_
protocol (mDNS, also used by Bonjour or ZeroConf). This protocol can then be
queried by other applications such as DNS clients or those that support
`DNS Service Discovery <https://en.wikipedia.org/wiki/Zero-configuration_networking#Service_discovery>`_
to find out and access services on the local network.

The ``debops.avahi`` Ansible role can be used to configure the Avahi service on
Debian or Ubuntu hosts. You can create custom services, publish static host
entries that point to other hosts on the local network, or even define and
publish CNAME records pointing to the host itself.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.avahi

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
