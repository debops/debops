.. _debops.etc_services:

debops.etc_services
===================

The ``debops.etc_services`` role can be used to "reserve" or "register" a
service port in the :file:`/etc/services` file. Service ports configured this way can
appear as named entries in many command outputs, such as :command:`iptables --list`
or :command:`netstat --listening --program`. You can also have convenient database
of reserved and free ports on a particular host, and reference ports by
their names in firewall configuration files.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/etc_services/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
