.. _debops.postgresql:

debops.postgresql
=================

`PostgreSQL`__ is a popular relational open source database. The
``debops.postgresql`` role can be used to create and manage PostgreSQL roles
and databases on local or remote PostgreSQL servers.

To manage the PostgreSQL server itself, you will need to use
``debops.postgresql_server`` role.

.. __: http://www.postgresql.org/

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

   .. literalinclude:: ../../../../ansible/roles/postgresql/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
