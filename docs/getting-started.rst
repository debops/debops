Getting started
===============

.. contents::
   :local:

Default setup
-------------

If you don't specify any configuration values, the role will setup a `nginx`_ instance
running a default installation of the latest Roundcube stable release which is then
accessible via ``https://roundcube.<your-domain>``. By default it will attach to a
local `MariaDB`_ instance for storing profile data of your Roundcube users.

Example inventory
-----------------

You can install Roundcube on a host by adding it to the ``[debops_roundcube]`` and the
``[debops_mariadb_server]`` (to setup the database instance) groups in your Ansible
inventory::

    [debops_roundcube]
    hostname

    [debops_mariadb_server]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``ansible-roundcube`` role to install Roundcube::

    ---

    - name: Setup Roundcube Webmail
      hosts: debops_roundcube

      roles:
        - role: ansible-roundcube
          tags: roundcube


.. _nginx: https://github.com/debops/ansible-nginx
.. _MariaDB: https://github.com/debops/ansible-mariadb
