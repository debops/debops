.. _debops.kmod:

debops.kmod
===========

The ``debops.kmod`` Ansible role can be used to manage configuration of the
Linux kernel modules, located in the :file:`/etc/modprobe.d/` directory, and
specify what kernel modules should be loaded at boot time using configuration
in :file:`/etc/modules-load.d/` directory.

Kernel module configuration can be specified using Ansible inventory, or other
Ansible roles can use the ``debops.kmod`` role to configure kernel module
options on their behalf.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.kmod/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
