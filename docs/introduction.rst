Introduction
============

This role installs a ownCloud_ instance on a specified host, either with
SQLite, MySQL, MariaDB or PostgreSQL database as a backend and an nginx
webserver as a frontend.

Only ownCloud 8.0 and later are supported because for older
versions there are no complete deb-packages available.

ownCloud will be installed as package coming directly from upstream.

.. _ownCloud: https://owncloud.org/


Features
~~~~~~~~

* LDAP setup.
* In memory caching using Redis for file locking and APCu.
* Fully automated ownCloud security updates.
* ownCloud theming support.
* Extensive configuration options via Ansible’s inventory.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.0``. To install it, run::

    ansible-galaxy install debops.owncloud

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
