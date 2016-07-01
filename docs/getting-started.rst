Getting started
===============

Example inventory
-----------------

To configure a NodeJS environment on a given host or set of hosts, they need to
be added to ``[debops_service_nodejs]`` Ansible group in the inventory::

    [debops_service_nodejs]
    hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nodejs`` role:

.. literalinclude:: playbooks/nodejs.yml
   :language: yaml

