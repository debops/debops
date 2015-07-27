Getting started
===============

.. contents::
   :local:

``debops.libvirt`` role is designed to use your normal admin account instead of
a ``root`` account for managing ``libvirt`` via it's API. That way Ansible can
access your own SSH keys through ``ssh-agent`` if necessary to connect to
remote ``libvirtd`` instances.

You should still use ``debops.libvirt`` with ``becone: True`` option in your
playbooks, it will automatically run tasks unprivileged when needed.

Because unprivileged account is used, role won't work correctly if that account
does not belong to ``libvirt`` group. On Ansible Controller this requires that
the user needs to log out and back in before new group takes effect. Role will
check if required group is present and won't run ``libvirt`` tasks otherwise to
not stop the playbook unnecessarily.

Use via local connection
~~~~~~~~~~~~~~~~~~~~~~~~

By default ``debops.libvirt`` will try to connect to a ``libvirtd`` system
instance on ``localhost`` (your user should be in ``libvirt`` system group to
be able to do this; ``debops.libvirtd`` role configures this automatically).

Network and storage pool configuration without specified ``item.uri`` parameter
applies to default connection. If your main ``libvirtd`` daemon is on
a different host, you can change the default connection using
``libvirt_default_uri`` variable.

Use via remote connections
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use ``debops.libvirt`` from your Ansible Controller host to centrally
configure ``libvirtd`` instances on remote hosts.

Use ``libvirt_connections`` dict variable to specify libvirt URI connections
with aliases, they will be configured in ``~/.config/libvirt/libvirt.conf`` on
account you use to run Ansible. After that, in each network or storage pool
definition add ``item.uri`` parameter with name of the connection to use for
that definition.

Example inventory
-----------------

To run this role in directly on ``libvirtd`` servers, they should be included
in ``[debops_libvirt]`` Ansible group::

    [debops_libvirt]
    hostname

If you want to use this role on your Ansible Controller, put it in the same
group as well::

    [debops_libvirt]
    hostname ansible_connection=local

Example playbook
----------------

Here's an example playbook which uses ``debops.libvirt`` role::

    ---

    - name: Configure libvirt service
      hosts: debops_libvirt
      tags: [ 'aspect::virtualization' ]
      become: False

      roles:
        - role: debops.libvirt
          tags: [ 'role::libvirt' ]

Ansible tags
~~~~~~~~~~~~

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
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

