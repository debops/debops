.. _debops.lvm:

debops.lvm
==========

`Logical Volume Manager`_ lets you manage your disk space in a more elastic
way, separating physical hard disks from the logical volumes.

This Ansible role lets you configure :file:`/etc/lvm/lvm.conf` configuration file,
as well as gives you a set of variables which can be used to manage LVM logical
volumes, automatically create filesystems on them and mount them as needed.

.. _Logical Volume Manager: https://en.wikipedia.org/wiki/Logical_Volume_Manager_(Linux)

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/lvm/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
