.. _debops.redis_server:

debops.redis_server
===================

`Redis <https://redis.io/>`__ is an in-memory key/value store, usable as
a persistent database, cache or a message broker.

The ``debops.redis_server`` Ansible role can be used to install and manage
Redis on Debian/Ubuntu hosts. Role supports management of multiple Redis
instances on a single host and is designed to cope with modifications done to
Redis configuration files at runtime.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   config-pipeline


Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.redis_server/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
