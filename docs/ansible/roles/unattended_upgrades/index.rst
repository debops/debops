.. _debops.unattended_upgrades:

debops.unattended_upgrades
==========================

The ``unattended-upgrades`` package manages `automatic, unattended upgrades
<https://wiki.debian.org/UnattendedUpgrades>`_ of the Debian-based hosts. You
can specify what package origins are included in the unattended upgrades, as
well as specify what packages should be exempt from the upgrades, among other
things.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/unattended_upgrades/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
