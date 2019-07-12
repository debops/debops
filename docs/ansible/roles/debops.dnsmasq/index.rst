.. _debops.dnsmasq:

debops.dnsmasq
==============

`dnsmasq`__ is an application that provides DNS, DHCP, TFTP and Router
Advertisement services in a compact package, suitable for small, internal
networks. it's commonly used as a DNS cache and forwarder on desktop
workstations or servers.

.. __: http://www.thekelleys.org.uk/dnsmasq/doc.html

The ``debops.dnsmasq`` Ansible role can be used to configure :command:`dnsmasq`
on a given host. By default the DNS cache will be configured, but the role
checks for presence of different services like ``lxc-net`` configured by the
:ref:`debops.lxc`, :command:`consul` and specific network interfaces defined by
the :ref:`debops.ifupdown`, and adjusts the configuration automatically.


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.dnsmasq/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
