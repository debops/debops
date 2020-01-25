.. _debops.stunnel:

debops.stunnel
==============

`stunnel`_ can be used to create encrypted TCP tunnels between two service
ports, either on the same host or on separate hosts.

Encryption is done using SSL certificates. This Ansible role can be used to
create tunnels between two or more hosts, using Ansible inventory groups.

.. _stunnel: http://stunnel.org/

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   guides
   troubleshooting

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/stunnel/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
