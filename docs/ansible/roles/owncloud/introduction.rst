Introduction
============

.. include:: ../../../includes/global.rst

This role installs a NextCloud_ or ownCloud_ instance on a specified host, either with
SQLite, MySQL, MariaDB or PostgreSQL database as a backend and an Nginx_
or Apache_ webserver as a frontend.

Nextcloud will be installed using the upstream tarballs. ownCloud will be installed as package coming directly from upstream.

Note that Nginx is `not officially supported by ownCloud nor NextCloud
<https://github.com/debops/ansible-owncloud/issues/49>`_ but it is community
supported and should work without problems. Apache is supported by the role but
not yet used by default and not very well tested.

Features
~~~~~~~~

* Support for LDAP using the :ref:`debops.ldap` Ansible role.
* In memory caching using Redis for file locking and APCu.
* Theming support (only tested with ownCloud 10).
* Extensive configuration options via Ansible’s inventory.
* Fully automated ownCloud security updates. `Not yet enabled by default nor tested with ownCloud 10 <https://github.com/debops/ansible-owncloud/issues/28>`_.

Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.1.4``. To install it, run::

    ansible-galaxy install debops.owncloud

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
