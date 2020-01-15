.. _debops.iscsi:

debops.iscsi
============

`Open-iSCSI`_ is a Linux iSCSI Initiator which can be used to connect to iSCSI
Targets to access block storage devices remotely as if they were connected
locally.

``debops.iscsi`` Ansible role allows you to configure the initiator, targets,
as well as create LVM Volume Groups from presented iSCSI LUNs and manage LVM
Logical Volumes.

.. _Open-iSCSI: http://open-iscsi.org/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/iscsi/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
