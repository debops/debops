.. _debops.salt:

debops.salt
===========

The ``debops.salt`` Ansible role can be used to install and configure
`SaltStack <https://saltstack.com/>`_ Master service. It is expected that Salt
Minions are installed using host deployment methods like PXE/preseeding, LXC
template scripts, etc. and contact the Salt Master service over DNS.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/salt/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
