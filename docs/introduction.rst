Introduction
============

.. include:: includes/all.rst

The ``debops.golang`` role can be used to setup a Go environment using
Debian/Ubuntu packages. It uses debops.apt_preferences_ role to
automatically install backported Go packages on older OS releases.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.golang

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
