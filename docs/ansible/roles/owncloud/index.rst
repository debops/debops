.. _debops.owncloud:

debops.owncloud
===============

This role installs a NextCloud__ or ownCloud__ instance on a specified host, either with
SQLite, MySQL, MariaDB or PostgreSQL database as a backend and an Nginx
or Apache webserver as a frontend.

.. __: https://nextcloud.com/
.. __: https://en.wikipedia.org/wiki/OwnCloud

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

.. toctree::
   :maxdepth: 2

   getting-started
   defaults-detailed
   external-users
   external-storage
   upgrade

.. only:: html

   .. toctree::
      :maxdepth: 2

      defaults/main
      ldap-dit

   Copyright
   ---------

   .. literalinclude:: ../../../../ansible/roles/owncloud/COPYRIGHT

..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
