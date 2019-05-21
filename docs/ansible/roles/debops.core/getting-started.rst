Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

By default ``debops.core`` is run from its own :file:`core.yml` DebOps playbook by
the :file:`common.yml` playbook, which means that it is run on all hosts in the
inventory.

If you want to modify the "root path" variables (``core__root_*``), it's best to
prepare the new ones before initial configuration (for example in a test
environment), so that you won't need to change them after everything is
configured.

To see what facts are configured on a host, run command:

.. code-block:: console

   user@host:~$ ansible <hostname> -s -m setup -a 'filter=ansible_local'

Ansible Controller IP addresses
-------------------------------

The ``debops.core`` role gathers information about the IP address(es) from which the
Ansible Controller host is connecting from using the ``$SSH_CLIENT`` environment
variable on the remote host.

The list of Ansible Controller IP addresses is accessible as
``ansible_local.core.ansible_controllers`` for other roles to use as
needed.

.. warning::

   For the IP address gathering to work correctly, you shouldn't specify
   ``become`` parameters in the Ansible inventory. In that case the playbook or
   task level setting won't be able to override the inventory setting and the
   IP address will be inaccessible to Ansible.

Example playbook
----------------

To get information about the IP address of the Ansible Controller,
``debops.core`` needs to be run from special playbook, which does not switch to
privileged mode by default, but the role within it does. That way, the role has
access to the environment variables of the unprivileged account Ansible is
connecting through and can read the ``$SSH_CLIENT`` environment variable and
get the IP address.

Note: Hosts provisioned by the ``bootstrap`` playbook have a workaround in
place so that the playbook could be run in privileged mode but to avoid
problems with `other provisioning methods <https://github.com/debops/ansible-core/issues/6#issuecomment-141923939>`_
the role should be run in unprivileged mode as mentioned.

This is a playbook that is used to run the role:

.. literalinclude:: ../../../../ansible/playbooks/service/core.yml
   :language: yaml

If you use your own set of custom playbooks, you can either copy the above
playbook, or, if you have the DebOps playbooks installed in the default location,
include the :file:`core.yml` playbook in your common playbook (it is sufficient to
run it only once at the start of the playbook):

.. code-block:: yaml

   ---

   - include: ~/.local/share/debops/debops-playbooks/playbooks/core.yml

   - name: Common playbook
     hosts: 'debops_all_hosts'
     become: True

     roles:

       - role: example-role

If you use the default DebOps playbooks alongside your own custom ones, you don't
need to include the :file:`core.yml` playbook at all.

See the usage guide in the ``debops.core`` documentation for information about
its use.
