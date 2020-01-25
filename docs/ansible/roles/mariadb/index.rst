.. _debops.mariadb:

debops.mariadb
==============

MariaDB__ is a popular relational SQL database that was forked from MySQL
server. Ansible roles ``debops.mariadb`` and ``debops.mariadb_server`` allow
you to manage a MariaDB server and / or access it remotely from other hosts.

``debops.mariadb`` role is the "client" part - it installs ``mariadb-client``
Debian package, and uses Ansible delegation to configure users and databases in
local or remote MariaDB servers. You can use ``debops.mariadb_server`` role to
manage the MariaDB server itself.

.. __: https://en.wikipedia.org/wiki/Mariadb

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   upgrade

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/mariadb/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
