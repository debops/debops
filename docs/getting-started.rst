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
      become: True

      roles:
        - role: debops.memcached
          tags: memcached

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::memcached``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::memcached``
  Execute all ``debops.memcached`` role dependencies in its context.

``depend::etc_services:memcached``
  Run ``debops.etc_services`` dependent role in ``debops.memcached`` context.

``depend::ferm:memcached``
  Run ``debops.ferm`` dependent role in ``debops.memcached`` context.
