.. _debops.icinga_web:

debops.icinga_web
=================

The `Icinga`__ project is a monitoring solution which can be used to monitor
infrastructure hosts and services. Icinga can use variety of remote agents as
well as SNMP to monitor remote hosts.

.. __: https://www.icinga.com/

DebOps provides support for Icinga 2, split into several roles:

- the :ref:`debops.icinga` role is the Icinga 2 Agent role, usually installed
  on all hosts in the cluster that should be monitored. Different instances can
  function as masters, satellites or clients depending on the configuration.

- the :ref:`debops.icinga_db` role can be used to configure the database
  support for Icinga 2, used by the web interface. Both PostgreSQL and MariaDB
  databases are supported.

- the :ref:`debops.icinga_web` role manages the Icinga 2 Web interface,
  including installation of external modules like Icinga 2 Director.


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main
   defaults-detailed


Copyright
---------

.. literalinclude:: ../../../../ansible/roles/icinga_web/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
