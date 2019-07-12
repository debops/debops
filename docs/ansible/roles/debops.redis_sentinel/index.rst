.. _debops.redis_sentinel:

debops.redis_sentinel
=====================

`Redis <https://redis.io/>`__ is an in-memory key/value store, usable as
a persistent database, cache or a message broker.
`Redis Sentinel <https://redis.io/topics/sentinel>`_ manages the failover and
high availability of a Redis cluster.

The ``debops.redis_sentinel`` Ansible role can be used to install and manage
multiple Redis Sentinel instances on Debian/Ubuntu hosts.

.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed
   config-pipeline


Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.redis_sentinel/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
