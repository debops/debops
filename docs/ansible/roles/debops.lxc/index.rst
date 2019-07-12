.. _debops.lxc:

debops.lxc
==========

`Linux Containers`__ or LXC provide a way to partition existing Linux hosts
into separate environments using Linux cgroups, namespace isolation, POSIX
capabilities and chrooted filesystems.

.. __: https://en.wikipedia.org/wiki/LXC

The ``debops.lxc`` Ansible role can be used to configure LXC support on
a Debian/Ubuntu host. It can manage configuration files in :file:`/etc/lxc/`
directory and provide custom scripts that allow, for example, initial
bootstrapping of the user's SSH public keys inside of the container so that it
can be managed remotely with Ansible.


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.lxc/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
