.. _debops.sysctl:

debops.sysctl
=============

The ``debops.sysctl`` Ansible role manages Linux kernel parameters.
It comes with kernel hardening and shared memory optimization enabled by
default.
The kernel hardening is ported from `hardening.os-hardening`__ for optimal
compatibility with DebOps.

.. __: https://github.com/hardening-io/ansible-os-hardening

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

   .. literalinclude:: ../../../../ansible/roles/sysctl/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
