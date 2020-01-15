.. _debops.atd:

debops.atd
==========

The :command:`at` and :command:`batch` commands can be used to compliment :program:`cron` and run
one-off tasks either at a specified time, or when the host CPU utilization is on
a low enough level.

The ``debops.atd`` role can be used to configure the :program:`atd` service, including
randomized load average threshold and randomized time between batch job
execution, as well as access control to the :command:`at` and ``batch`` commands by
the users.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/atd/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
