Getting started
===============

Ansible local facts
-------------------

The :ref:`debops.golang` role provides a set of Ansible local facts at the
``ansible_local.golang.*`` namespace. The facts can be used to determine the
location of the Go application binaries - installation from APT package or from
source can result in different binary location (:file:`/usr/bin/` vs
:file:`/usr/local/bin/`) which might require different path specification in
:command:`systemd` unit files, for example.


Example inventory
-----------------

To configure a Go environment on a given host or set of hosts, they need to
be added to ``[debops_service_golang]`` Ansible group in the inventory:

.. code-block:: none

   [debops_service_golang]
   hostname

The role will install Go development environment by default if no other Go
packages are defined via :envvar:`golang__dependent_packages` variable, by
other Ansible roles.


Example playbook
----------------

If you are using this role without DebOps, or you want to use it as
a dependency for another Ansible role, here's an example Ansible playbook that
uses the ``debops.golang`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/golang.yml
   :language: yaml
