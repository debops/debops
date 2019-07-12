.. _debops.rsnapshot:

debops.rsnapshot
================

The `rsnapshot`__ script is a wrapper around the `rsync`__ command that allows
creation and management of snapshotted backups of local or remote filesystems.
Periodic snapshots are created using :command:`cron` jobs and use `hard
links`__ to perform deduplication.

The ``debops.rsnapshot`` Ansible role acts as another "layer" above
:command:`rsnapshot`. The role can configure snapshotted backups of the local
host to internal or removable storage, as well as create snapshotted backups of
remote hosts over SSH.

.. __: https://rsnapshot.org/
.. __: https://rsync.samba.org/
.. __: https://en.wikipedia.org/wiki/Hard_link

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   guides

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.rsnapshot/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
