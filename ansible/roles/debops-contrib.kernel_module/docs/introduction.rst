Introduction
============

.. include:: includes/all.rst

The ``debops-contrib.kernel_module`` role allows you to manage Linux kernel modules.

Features
~~~~~~~~

* Module blacklisting
* Module loading (with optional parameters)
* Optionally forces that a module is loaded with certain parameters by unloading it first.
* Either make changes permanent or only to the running system. Default is permanent.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.3``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops-contrib.kernel_module

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
