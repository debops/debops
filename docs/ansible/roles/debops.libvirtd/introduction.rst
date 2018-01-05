Introduction
============

``debops.libvirtd`` Ansible role manages the `libvirtd`_ daemon on
a virtualization host (server side). It will automatically install QEMU KVM
support on any host that is not a KVM guest, to allow for easy deployment of
KVM virtual machines.

Configuration of :program:`libvirtd` instance (local or remote) can be performed using
:ref:`debops.libvirt` role, which uses the ``libvirt`` API to manage the server.

.. _libvirtd: https://libvirt.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.3``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.libvirtd

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
