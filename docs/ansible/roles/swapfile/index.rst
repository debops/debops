.. _debops.swapfile:

debops.swapfile
===============

This Ansible role lets you manage one or multiple swap files. You can also
manage kernel parameters related to how swap is used by the system.

Note that this role can not setup a swap file on a BTRFS filesystem.

Refer to :ref:`debops.sysctl` for paging and swapping related kernel settings.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   upgrade

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/swapfile/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
