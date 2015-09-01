Introduction
============

This Ansible role manages GRUB configuration. It detects kernel parameters
which are currently set (probably during installation). Autodetected
parameters can be merged or overwritten by Ansible variables. It can also
enable both Linux kernel and GRUB serial console.

Parameter autodetection with values that contain spaces is not supported.

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
