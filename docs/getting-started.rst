Getting started
===============

.. contents::
   :local:

Default setup
-------------

If you don't specify any configuration values, the role will setup a `nginx`_ instance
running a default installation of the latest Roundcube stable release which is then
accessible via ``https://roundcube.<your-domain>``.

Example inventory
-----------------

You can install Roundcube on a host by adding it to the ``[debops_roundcube]`` group
groups in your Ansible inventory::

    [debops_roundcube]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops-contrib.roundcube`` role to install
Roundcube::

    ---

    - name: Manage Roundcube Webmail
      hosts: [ 'debops_service_roundcube', 'debops_roundcube' ]

      roles:
        - role: debops-contrib.roundcube
          tags: [ 'role::roundcube' ]


.. _nginx: https://github.com/debops/ansible-nginx
