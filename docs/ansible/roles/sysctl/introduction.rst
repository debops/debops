Introduction
============

.. include:: ../../../includes/global.rst

The ``debops.sysctl`` Ansible role manages Linux kernel parameters.
It comes with kernel hardening and shared memory optimization enabled by
default.
The kernel hardening is ported from hardening.os-hardening_ for optimal
compatibility with DebOps.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.2.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.sysctl

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
