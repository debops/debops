Getting started
===============

.. contents::
   :local:

Example inventory
-----------------

The ``debops.ferm`` role is part of the default DebOps playbook an run on
all hosts which are part of the ``[debops_all_hosts]`` group. To use this
role with DebOps it's therefore enough to add your host to the mentioned
host group (which most likely it is already)::

    [debops_all_hosts]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops.ferm`` role::

    ---

    - name: Manage iptables rules with ferm
      hosts: [ 'debops_service_ferm' ]

      roles:
        - role: debops.ferm
          tags: role::ferm

