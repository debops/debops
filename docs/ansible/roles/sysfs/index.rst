.. _debops.sysfs:

debops.sysfs
============

`sysfs <https://en.wikipedia.org/wiki/Sysfs>`_ is a Linux kernel virtual
filesystem, usually mounted at :file:`/sys`. It provides a file-based interface
to the kernel data structures related to hardware and host configuration. The
filesystem entries can be manipulated by the :command:`sysfsutils` package
provided by Debian/Ubuntu.

The ``debops.sysfs`` Ansible role can be used to configure ``sysfs`` attributes
in supported environments. It can be used as a standalone role, or a dependent
role to configure ``sysfs`` on behalf of another Ansible role.

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

   .. literalinclude:: ../../../../ansible/roles/sysfs/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
