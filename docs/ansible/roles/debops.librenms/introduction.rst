Introduction
============

`LibreNMS`_ is a network monitoring dashboard written in PHP. It can use SNMP,
:program:`collectd`, :program:`check_mk` or other agents to gather data from variety of
devices (switches, routers, servers, etc.) and graph them using RRD. It's easy
to use, and can perform autodiscovery to find and monitor additional devices.

``debops.librenms`` role will manage a central LibreNMS monitoring host and web
interface.

.. _LibreNMS: http://www.librenms.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.librenms

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
