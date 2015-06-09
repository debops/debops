Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

To install ``memcached`` on a host, you can add it in ``[debops_memcached]``
Ansible group::

    [debops_memcached]
    hostname

Example playbook
----------------

Here's an example playbook which uses ``debops.memcached`` role::

    ---

    - name: Install memcached service
      hosts: debops_memcached
      sudo: True

      roles:
        - role: debops.memcached
          tags: memcached

