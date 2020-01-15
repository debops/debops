.. _debops.grub:

debops.grub
===========

This Ansible role manages GRUB configuration. It detects kernel parameters
which are currently set (probably during installation). Autodetected
parameters can be merged or overwritten by Ansible variables.
It can also enable both Linux kernel and GRUB serial console.

Parameter autodetection with values that contain spaces is not supported.

Additionally, this role allows you to configure password protection for GRUB.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/grub/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
