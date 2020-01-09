Getting started
===============

.. contents::
   :local:

The ``debops.libvirt`` role is designed to use your normal admin account instead of
a ``root`` account for managing ``libvirt`` via it's API. That way Ansible can
access your own SSH keys through :command:`ssh-agent` if necessary to connect to the
remote :program:`libvirtd` instances.

You should still use ``debops.libvirt`` with the ``become: True`` option in your
playbooks, it will automatically run tasks unprivileged when needed.

Because an unprivileged account is used, the role won't work correctly if that
account does not belong to the ``libvirt`` group. On the Ansible Controller this
requires that the user needs to log out and back in before the new group takes
effect. This role will check if the required group is present and won't run
``libvirt`` tasks otherwise to not stop the playbook unnecessarily.

Use via local connection
------------------------

By default ``debops.libvirt`` will try to connect to a :program:`libvirtd` system
instance on ``localhost``. Your user should be in the ``libvirt`` system group
to be able to do this. The ``debops.libvirtd`` role configures this automatically.

Network and storage pool configuration without specified ``item.uri`` parameter
applies to default connection. If your main :program:`libvirtd` daemon is on
a different host, you can change the default connection using the
``libvirt__default_uri`` variable.

Use via remote connections
--------------------------

You can use ``debops.libvirt`` from your Ansible Controller host to centrally
configure :program:`libvirtd` instances on remote hosts.

Use the ``libvirt__connections`` dict variable to specify libvirt URI connections
with aliases, they will be configured in ``~/.config/libvirt/libvirt.conf`` on
the account you use to run Ansible. After that, in each network or storage pool
definition add ``item.uri`` parameter with the name of the connection to use for
that definition.

Example inventory
-----------------

To run this role directly on :program:`libvirtd` servers, they should be included
in the ``[debops_libvirt]`` Ansible group::

    [debops_service_libvirt]
    hostname

If you want to use this role on your Ansible Controller, put it in the same
group as well::

    [debops_service_libvirt]
    hostname ansible_connection=local

Example playbook
----------------

Here's an example playbook which uses the ``debops.libvirt`` role::

    ---

    - name: Manage libvirt hosts
      hosts: [ 'debops_service_libvirt' ]
      become: True

      roles:
        - role: debops.libvirt
          tags: [ 'role::libvirt' ]


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after the host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::libvirt``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::libvirt:networks``
  Configure ``libvirt`` networks.

``role::libvirt:pools``
  Configure ``libvirt`` storage pools.

