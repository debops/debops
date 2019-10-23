.. _debops.mcli:

debops.mcli
===========

`MinIO`__ is an Open Source Amazon Simple Storage Service (S3) compatible
object storage service. The `MinIO Client`__ application is used to interface
with MinIO and perform various administrative tasks, including extended
configuration of the service.

.. __: https://min.io/
.. __: https://docs.min.io/docs/minio-client-complete-guide

The ``debops.mcli`` Ansible role installs MinIO Client binary on a Debian or
Ubuntu host either by downloading and verifying it from the upstream repository
directly, or cloning the source code and building it locally.

The MinIO Client binary will be installed as the :command:`mcli` binary instead
of the :command:`mc` binary preferred by upstream to avoid clashing with the
``mc`` Debian package which provides Midnight Commander. This solution `is
suggested by upstream`__ as well.

.. __: https://github.com/minio/mc/blob/master/CONFLICT.md

You can use the :ref:`debops.minio` Ansible role to install and configure the
MinIO service itself.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.mcli/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
