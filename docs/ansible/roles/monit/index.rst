.. _debops.monit:

debops.monit
============

`Monit <https://mmonit.com/monit/>`_ is a service monitoring daemon. It can be
used to monitor processes, files, system and remote hosts, and if necessary,
take configured actions when specific parameters change, like restarting
services and notifying the system administrator.

This role can be used to configure Monit on a host. It will automatically
detect selected services and configure checks for them.

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

   .. literalinclude:: ../../../../ansible/roles/monit/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
