.. _debops.proc_hidepid:

debops.proc_hidepid
===================

This role will ensure that the ``/proc`` filesystem is mounted with the
``hidepid=`` option enabled. `The 'hidepid=' option`__ can be used to hide
processes that don't belong to a particular user account.

.. __: https://wiki.archlinux.org/index.php/Security#hidepid

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.proc_hidepid/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
