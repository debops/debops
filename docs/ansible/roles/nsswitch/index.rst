.. _debops.nsswitch:

debops.nsswitch
===============

The ``debops.nsswitch`` Ansible role can be used to configure the Name Service
Switch using the :file:`/etc/nsswitch.conf` configuration file. The role can be
used as a dependency of another Ansible role to allow management of NSS
services after they have been configured. System administrators can use this
role to enable or disable NSS services conditionally or change the preferred
order of the NSS services.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/nsswitch/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
