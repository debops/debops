Getting started
===============

Example inventory
-----------------

To configure a Go environment on a given host or set of hosts, they need to
be added to ``[debops_service_golang]`` Ansible group in the inventory:

.. code-block:: none

   [debops_service_golang]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.golang`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/golang.yml
   :language: yaml
