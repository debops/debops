Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:


The ``debops.libvirtd`` role will install :program:`libvirtd` along with virtualization
components required on the server.

Configuration at the moment is very minimal - specified account will be granted
access to ``libvirt`` system group which has access to :program:`libvirtd` daemon. If
more configuration is required, it will be added at a later time.


Example inventory
-----------------

This role should be enabled on virtualization hosts, you can do this by adding
a host to the ``[debops_service_libvirtd]`` group:

.. code:: ini

   [debops_service_libvirtd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.libvirtd`` role:

.. literalinclude:: playbooks/libvirtd.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::libvirtd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
