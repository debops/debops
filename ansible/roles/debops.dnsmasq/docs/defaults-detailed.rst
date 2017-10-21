Default variable details
========================

Some of ``debops.dnsmasq`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. dnsmasq__dhcp_hosts:

dnsmasq__dhcp_hosts
-------------------
:envvar:`dnsmasq__dhcp_hosts` must be a list of hosts. Each host is a dictionary
consisting of a ``name``, a ``mac`` address, an :command:`ip` address and optionally a
``lease_time``; by default it's 1 day (``1d``).:

.. code-block:: yaml

   dnsmasq__dhcp_hosts:
     - name: client
       mac: '01:23:45:67:89:ab'
       ip: '192.168.0.42'
       # optional; default: 1d
       lease_time: 12h
