.. _debops.libvirtd:

debops.libvirtd
===============

``debops.libvirtd`` Ansible role manages the `libvirtd`_ daemon on
a virtualization host (server side). It will automatically install QEMU KVM
support on any host that is not a KVM guest, to allow for easy deployment of
KVM virtual machines.

Configuration of :program:`libvirtd` instance (local or remote) can be performed using
:ref:`debops.libvirt` role, which uses the ``libvirt`` API to manage the server.

.. _libvirtd: https://libvirt.org/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/libvirtd/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
