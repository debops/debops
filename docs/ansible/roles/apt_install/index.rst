.. _debops.apt_install:

debops.apt_install
==================

The ``debops.apt_install`` Ansible role is meant to be used as an easy way to
install APT packages on hosts that don't require more extensive configuration
which would require a more extensive, custom Ansible role. The role itself
exposes several Ansible default variables which can be used to specify custom
lists of packages on different levels of Ansible inventory (global, per-group
or per-host).

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/apt_install/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
