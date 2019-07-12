.. _debops.apt_mark:

debops.apt_mark
===============

The ``debops.apt_mark`` Ansible role can be used to set the desired state of
APT packages using :man:`apt-mark(8)` command. It might be useful if a new
Debian/Ubuntu install results in many packages which should be installed are
marked for autoremoval, or if you want to hold certain APT packages in their
current state. The role operates only on packages that are already installed.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.apt_mark/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
