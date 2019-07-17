.. _debops.wpcli:

debops.wpcli
============

`WP-CLI`__ framework is a PHP script which can be used to manage `WordPress`__
installations via the Linux shell. It provides a command line interface to WP
Admin dashboard, provides an interface for :command:`cron` task execution for
a given WordPress website, create backups, and lots of other things.

.. __: https://wp-cli.org/
.. __: https://wordpress.org/

The ``debops.wpcli`` Ansible role can be used to install WP-CLI on a host
managed by DebOps, which in turn enables management of per-user WordPress
websites. The role is designed with shared hosting environment in mind; users
need to utilize other DebOps/Ansible roles to manage the :ref:`webserver
<debops.nginx>`, :ref:`database engine <debops.mariadb_server>`, :ref:`PHP
environment <debops.php>` and :ref:`UNIX accounts <debops.users>`, etc.


.. toctree::
   :maxdepth: 2

   getting-started
   defaults/main

Copyright
---------

.. literalinclude:: ../../../../ansible/roles/debops.wpcli/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
