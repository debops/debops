Introduction
============

`sysfs <https://en.wikipedia.org/wiki/Sysfs>`_ is a Linux kernel virtual
filesystem, usually mounted at :file:`/sys`. It provides a file-based interface
to the kernel data structures related to hardware and host configuration. The
filesystem entries can be manipulated by the :command:`sysfsutils` package
provided by Debian/Ubuntu.

The ``debops.sysfs`` Ansible role can be used to configure ``sysfs`` attributes
in supported environments. It can be used as a standalone role, or a dependent
role to configure ``sysfs`` on behalf of another Ansible role.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.sysfs

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
