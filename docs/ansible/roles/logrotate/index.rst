.. _debops.logrotate:

debops.logrotate
================

The ``logrotate`` package is used to periodically rotate logs, so that they
don't fill up the disk space on the filesystem. Rotated logs can be moved to
a different host or emailed before removal for archival purposes.

The ``debops.logrotate`` Ansible role allows you to manage log rotation
configuration for system packages, or create custom log configuration. The role
can be used by other roles as a dependency to make automatic ``logrotate``
configuration easier.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/logrotate/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
