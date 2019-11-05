.. _custom_environment:

Custom environment variables
============================

In certain situations, for example on a network where direct Internet access is
not allowed and users are required to use a HTTP proxy, you might need to
define a custom set of environment variables for Ansible to execute playbooks.
The DebOps playbooks allow you to do that using a set of Ansible inventory
variables which should be defined as YAML dictionaries:

``inventory__environment``
  This variable is meant to set environment variables on all hosts in Ansible
  inventory.

``inventory__group_environment``
  This variable is meant to be used on a group of hosts in Ansible inventory.
  Only one group is supported.

``inventory__host_environment``
  This variable is meant to set environment variables on specific hosts in
  Ansible inventory.

The configured environment variables will be active in all of the DebOps
playbooks included in this repository. The more specific variables override the
more general ones, just like normal Ansible variables.

The environment variables defined using these YAML dictionaries only have
effect during the :command:`ansible-playbook` run.
Normal :command:`ansible` commands as well as commands/services executed on
remote hosts will not use them.
To configure desired environment variables on remote hosts,
you might want to check the :ref:`debops.environment` role.

Examples
--------

To configure a HTTP proxy which should be used by Ansible roles on all hosts,
add in the :file:`ansible/inventory/group_vars/all/inventory.yml` file:

.. code-block:: yaml

   inventory__environment:
     http_proxy: 'http://proxy.{{ ansible_domain }}:3128'

To add support for these variables in your own playbooks, make sure that they
contain the following code:

.. code-block:: yaml

   - name: Configure a custom service
     hosts: [ 'debops_service_custom' ]
     become: True

     environment: '{{ inventory__environment | d({})
                      | combine(inventory__group_environment | d({}))
                      | combine(inventory__host_environment  | d({})) }}'

     roles:

       - role: custom-role
         tags: [ 'role::custom' ]
