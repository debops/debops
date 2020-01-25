.. _debops.tcpwrappers:

debops.tcpwrappers
==================

The ``debops.tcpwrappers`` Ansible role can be used to manage entries in
``/etc/hosts.allow`` and ``/etc/hosts.deny`` which are used by TCP Wrappers to
limit connections to daemons that utilize the ``libwrap`` library.

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

   .. literalinclude:: ../../../../ansible/roles/tcpwrappers/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
