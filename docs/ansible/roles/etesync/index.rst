.. _debops.etesync:

debops.etesync
==============

Deploys a `EteSync`_ server. EteSync is a cross-platform project to provide
secure, end-to-end encrypted, and privacy respecting sync for your contacts,
calendars and tasks.

Note that the role only sets up the "API" server without the user web interface
that can be used to edit contacts and calendars in a browser. Therefore, after
the setup is completed, you will need to use a EteSync client program to work
with the service. The only "graphical" interface provided is the administration
web interface, that you can use to manage EteSync users (available under
``/admin``).

.. _EteSync: https://www.etesync.com/

.. toctree::
   :maxdepth: 2

   getting-started

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/etesync/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
