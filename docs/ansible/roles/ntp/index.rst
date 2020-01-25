.. _debops.ntp:

debops.ntp
==========

An NTP daemon is used for time synchronization, either on a local system as
a client, or on remote systems as a server.

The ``debops.ntp`` Ansible role supports multiple NTP servers, and is
container-aware so that an NTP server won't be installed inside containers.

The role is also used to configure the system timezone using the ``tzdata``
package.

.. toctree::
   :maxdepth: 2

   getting-started

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/ntp/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
