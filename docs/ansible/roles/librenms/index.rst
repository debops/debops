.. _debops.librenms:

debops.librenms
===============

`LibreNMS`_ is a network monitoring dashboard written in PHP. It can use SNMP,
:program:`collectd`, :program:`check_mk` or other agents to gather data from variety of
devices (switches, routers, servers, etc.) and graph them using RRD. It's easy
to use, and can perform autodiscovery to find and monitor additional devices.

``debops.librenms`` role will manage a central LibreNMS monitoring host and web
interface.

.. _LibreNMS: http://www.librenms.org/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/librenms/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
