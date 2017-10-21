Introduction
============

.. include:: includes/all.rst

MariaDB_ is a popular relational SQL database that was forked from MySQL
server. Ansible roles ``debops.mariadb`` and debops.mariadb_server_ allow
you to manage a MariaDB server and / or access it remotely from other hosts.

``debops.mariadb`` role is the "client" part - it installs ``mariadb-client``
Debian package, and uses Ansible delegation to configure users and databases in
local or remote MariaDB servers. You can use debops.mariadb_server_ role to
manage the MariaDB server itself.

Installation
~~~~~~~~~~~~

You can install this role using Ansible Galaxy:

.. code-block:: console

   user@host:~$ ansible-galaxy install debops.mariadb

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
