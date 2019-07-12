.. _debops.tftpd:

debops.tftpd
============

This Ansible role can configure a standalone TFTP server using the
:command:`tftpd-hpa` daemon. The TFTP server can be used to serve files for
embedded devices or serve iPXE files from :ref:`debops.ipxe` role to other
hosts on the network, allowing for network boot and OS installation.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.tftpd/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
