.. _debops.libvirt:

debops.libvirt
==============

The ``debops.libvirt`` role can be used to manage networks and storage pools
defined in `libvirt`_ virtualization service. It's designed to be used either
"locally", directly on a given host, or "remotely" from a central host through
the API.

To configure a host to provide the :program:`libvirtd` service you can use the
``debops.libvirtd`` role.

.. _libvirt: https://libvirt.org/

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

   .. literalinclude:: ../../../../ansible/roles/libvirt/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
