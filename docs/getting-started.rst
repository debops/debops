Getting started
===============

.. contents::
   :local:

The ``debops.libvirtd`` role will install ``libvirtd`` along with virtualization
components required on the server.

Configuration at the moment is very minimal - specified account will be granted
access to ``libvirt`` system group which has access to ``libvirtd`` daemon. If
more configuration is required, it will be added at a later time.

Example inventory
-----------------

This role should be enabled on virtualization hosts, you can do this by adding
a host to ``[debops_libvirtd]`` group.

    [debops_libvirtd]
    hostname

Example playbook
----------------

Here's an example playbook which uses the ``debops.libvirtd`` role::

    ---

    - name: Configure libvirtd service
      hosts: debops_libvirtd
      tags: [ 'aspect::virtualization' ]
      sudo: True

      roles:
        - role: debops.libvirtd
          tags: [ 'role::libvirtd' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::libvirtd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

