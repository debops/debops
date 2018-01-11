Introduction
============

This Ansible role lets you manage one or multiple swap files. You can also
manage kernel parameters related to how swap is used by the system.

Note that this role can not setup a swap file on a BTRFS filesystem.

Refer to :ref:`debops.sysctl` for paging and swapping related kernel settings.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.swapfile

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
