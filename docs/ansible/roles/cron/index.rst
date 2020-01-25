.. _debops.cron:

debops.cron
===========

The ``debops.cron`` Ansible role can be used to manage :program:`cron` jobs
through Ansible inventory. You can define :program:`cron` jobs at different
levels of Ansible inventory (all hosts, a group of hosts, specific hosts) and
manage custom files or scripts required by the jobs.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/cron/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
