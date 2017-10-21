Introduction
============

This Ansible role will allow you to configure iSCSI Targets on specified hosts
using `tgt`_ package. You can create and remove specific iSCSI Targets without
distrupting the connections of other targets. Only targets that are unused will
be modified during normal operation. `debops.ferm`_ role will be used to manage
``iptables`` firewall to allow access from all or specific hosts or networks.

.. _tgt: http://stgt.sourceforge.net/
.. _debops.ferm: https://github.com/debops/ansible-ferm/

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
