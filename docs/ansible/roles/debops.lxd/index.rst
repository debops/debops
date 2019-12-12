.. _debops.lxd:

debops.lxd
==========

`Linux Containers`__ or LXC provide a way to partition existing Linux hosts
into separate environments using Linux cgroups, namespace isolation, POSIX
capabilities and chrooted filesystems.

.. __: https://en.wikipedia.org/wiki/LXC

`LXD`__, or a Linux Container Daemon, is a service written in Go which provides
a REST API and CLI interface for Linux Container management.

.. __: https://linuxcontainers.org/lxd/introduction/

The ``debops.lxd`` Ansible role can be used to install and configure the LXD
service on a Debian or Ubuntu hosts. The role will use the :ref:`debops.golang`
role to install the :command:`lxd` and :command:`lxc` binaries from upstream on
Debian hosts.


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.lxd/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
