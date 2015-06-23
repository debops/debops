Introduction
============

`MariaDB`_ is a popular relational SQL database that was forked from MySQL
server. Ansible roles ``debops.mariadb`` and ``debops.mariadb_server`` allow
you to manage a MariaDB server and / or access it remotely from other hosts.

``debops.mariadb`` role is the "client" part - it installs ``mariadb-client``
Debian package, and uses Ansible delegation to configure users and databases in
local or remote MariaDB servers. You can use ``debops.mariadb_server`` role to
manage the MariaDB server itself.

.. _MariaDB: http://mariadb.org/

Installation
~~~~~~~~~~~~

You can install this role using Ansible Galaxy::

    ansible-galaxy install debops.mariadb

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
