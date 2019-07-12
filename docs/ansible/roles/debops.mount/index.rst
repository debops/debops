.. _debops.mount:

debops.mount
============

The ``debops.mount`` Ansible role can be used to manage local filesystem mounts
as well as bind mounts in the :file:`/etc/fstab` database. Custom directories
can also be created by this role, with support for normal as well as ACL
attributes.

This role is meant to be used to configure local filesystems, for remote
filesystems, you can use the :ref:`debops.nfs` role instead, which will
configure the NFS client service.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.mount/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
