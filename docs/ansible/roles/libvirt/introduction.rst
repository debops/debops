Introduction
============

The ``debops.libvirt`` role can be used to manage networks and storage pools
defined in `libvirt`_ virtualization service. It's designed to be used either
"locally", directly on a given host, or "remotely" from a central host through
the API.

To configure a host to provide the :program:`libvirtd` service you can use the
``debops.libvirtd`` role.

.. _libvirt: https://libvirt.org/

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run::

    ansible-galaxy install debops.libvirt

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
