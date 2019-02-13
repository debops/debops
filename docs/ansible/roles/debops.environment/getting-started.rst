Getting started
===============

.. contents:: Sections
   :local:

.. _environment__ref_inventory__environment:

Usage with inventory__environment
---------------------------------

The DebOps playbooks use a set of Ansible inventory variables to provide custom
environment during the playbook execution. These are YAML dictionary variables:

- ``inventory__environment``
- ``inventory__group_environment``
- ``inventory__host_environment``

The ``debops.environment`` includes contents of these variables in its own
``environment__default_variables`` list, which is then added to the
``/etc/environment`` file on each host. Other variable lists described below
can override these environment variables if necessary.

The ``inventory__*_environment`` variables are the best place to set variables
if you want to have the same environment during Ansible playbook execution and
on the host itself over ``ssh`` or via ``cron``, etc. See the documentation  of
`inventory__variables <https://docs.debops.org/en/latest/debops-playbooks/custom-environment.html>`_
for more details.


Ansible inventory layout
------------------------

The role uses multiple lists of variables which can be defined in Ansible
inventory:

``environment__variables``
  This list can be defined in ``inventory/group_vars/all/environment.yml`` file
  to define variables that should be set on all hosts in the inventory.

``environment__group_variables``
  This list can be defined in a specific group, for example
  ``inventory/group_vars/<group_name>/environment.yml`` to set variables on
  a group of hosts. Only one "level" of such variables is supported.

``environment__host_variables``
  This list can be defined for a specific host, for example in
  ``inventory/host_vars/<hostname>/environment.yml`` file, to set variables
  only on that host.

The environment variables set in above lists are combined in above order,
therefore more specific variables will "mask" more general ones, just like
Ansible inventory variables. If you remove already set variables, they will be
automatically removed on the corresponding hosts as well on the next Ansible
playbook run.


Usage as a role dependency
--------------------------

Other roles can use ``debops.environment`` role in their own playbooks to
idempotently set environment variables in ``/etc/environment`` file. Variables
set in this way (using ``environment__dependent_variables`` list) will be
stored in Ansible local facts on the affected hosts so that they will be
preserved on subsequent Ansble runs. They will not be removed automatically.

The variables defined by roles override variables defined through Ansible
inventory.


Example inventory
-----------------

The ``debops.environment`` role is included in the ``common.yml`` DebOps
playbook, therefore you don't need to add a host to specific group to use it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.environment`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/environment.yml
   :language: yaml
