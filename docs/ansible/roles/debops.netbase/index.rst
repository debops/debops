.. _debops.netbase:

debops.netbase
==============

The ``debops.netbase`` Ansible role manages the hostname stored in
:file:`/etc/hostname`, as well as the local host and network database located
in :file:`/etc/hosts` and :file:`/etc/networks` files, respectively.  It can be
used as a substitute for a DNS service for small number of hosts; with bigger
network or larger clusters usage of a real DNS server is preferred.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.netbase/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
