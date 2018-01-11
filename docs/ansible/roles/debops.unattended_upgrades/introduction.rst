Introduction
============

The ``unattended-upgrades`` package manages `automatic, unattended upgrades
<https://wiki.debian.org/UnattendedUpgrades>`_ of the Debian-based hosts. You
can specify what package origins are included in the unattended upgrades, as
well as specify what packages should be exempt from the upgrades, among other
things.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.0.0``. To install it, run:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.unattended_upgrades

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
