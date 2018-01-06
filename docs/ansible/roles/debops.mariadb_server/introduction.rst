Introduction
============

.. include:: ../../../includes/global.rst

MariaDB_ is a popular relational SQL database that was forked from MySQL
server. Ansible roles :ref:`debops.mariadb` and ``debops.mariadb_server`` allow
you to manage a MariaDB server and / or access it remotely from other hosts.

``debops.mariadb_server`` role is the "server" part - it installs
``mariadb-server`` Debian package, and configures access to the database from
local ``root`` account. After that, you can use :ref:`debops.mariadb` role to
manage databases and user accounts on the server.

Installation
~~~~~~~~~~~~

You can install this role using Ansible Galaxy::

    ansible-galaxy install debops.mariadb_server

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
