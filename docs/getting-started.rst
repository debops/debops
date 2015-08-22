Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

By default ``debops.core`` is run from its own ``core.yml`` DebOps playbook by
the ``common.yml`` playbook, which means that it is run on all hosts in the
inventory.

If you want to modify the "root path" variables (``core_root_*``), it's best to
prepare the new ones before initial configuration (for example in a test
environment), so that you won't need to change them after everything is
configured.

To see what facts are configured on a host, run command::

    ansible <hostname> -s -m setup -a 'filter=ansible_local'

Ansible Controller IP addresses
-------------------------------

``debops.core`` role gathers information about IP address from which the
Ansible Controller host is connecting, using ``$SSH_CLIENT`` environment
variable on remote host.

List of Ansible Controller IP addresses is stored in
``ansible_local.core.ansible_controllers`` list for other roles to use as
needed.

Example playbook
----------------

To get information about the IP address of the Ansible Controller,
``debops.core`` needs to be run from special playbook, which does not switch to
privileged mode by default, but the role within it does. That way, role has
access to the environment variables of the unprivileged account Ansible is
connecting through and can read the ``$SSH_CLIENT`` environment variable and
get the IP address.

This is a playbook that is used to run the role::

    ---
    - name: Prepare core environment
      hosts: 'all:!localhost'
      become: False

      roles:

        - role: debops.core
          tags: [ 'role::core' ]
          become: True

If you use your own set of custom playbooks, you can either copy the above
playbook, or, if you have DebOps playbooks installed in the default location,
include the ``core.yml`` playbook in your common playbook (it is sufficient to
run it only once at the start of the playbook)::

    ---

    - include: ~/.local/share/debops/debops-playbooks/playbooks/core.yml

    - name: Common playbook
      hosts: all:!localhost
      become: True

      roles:

        - role: example-role

If you use default DebOps playbooks alongside your own custom ones, you don't
need to include the ``core.yml`` playbook at all.

See the usage guide in the ``debops.core`` documentation for information about
its use.

