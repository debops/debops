Introduction
============

.. include:: includes/all.rst

This role installs a ownCloud_ instance on a specified host, either with
SQLite, MySQL, MariaDB or PostgreSQL database as a backend and an nginx
webserver as a frontend.

ownCloud will be installed as package coming directly from upstream.

Note that Nginx is `not officially supported by ownCloud nor NextCloud <https://github.com/debops/ansible-owncloud/issues/49>`_ but it is community supported and should work without problems. Apache is supported by the role but not yet used by default.

Features
~~~~~~~~

* LDAP setup.
* In memory caching using Redis for file locking and APCu.
* ownCloud theming support.
* Extensive configuration options via Ansible’s inventory.
* Fully automated ownCloud security updates. `Not yet enabled by default <https://github.com/debops/ansible-owncloud/issues/28>`_.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.4``. To install it, run::

    ansible-galaxy install debops.owncloud

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
