Getting started
===============

.. contents::
   :local:


Initial configuration
---------------------

The default :command:`radvd` installation does not set up any configuration
file, and the service does not start correctly without proper configuration in
place.

The ``debops.radvd`` role will try and autogenerate a :command:`radvd`
configuration based on the host environment. Any bridge interfaces with global
IPv6 addresses will be enabled by default and included in the configuration. If
you don't have any valid bridges with IPv6 addresses, the role execution will
fail because the role will try and restart :command:`radvd` service on
configuration changes.

To avoid the issues with initial configuration, you should ensure that hosts on
which you install :command:`radvd` have proper network configuration. You can
use the :ref:`debops.ifupdown` role to create a virtual network bridge or,
alternatively, create :command:`radvd` configuration for any existing
interfaces. For example, to offer Router Advertisements on a private, internal
network, you can add this configuration to your Ansible inventory:

.. code-block:: yaml

   radvd__interfaces:

     - name: 'eth1'
       options:
         - 'AdvSendAdvert': True
         - 'IgnoreIfMissing': True
       prefixes:
         - name: '::/64'
           options:
             - 'AdvOnLink': True
             - 'AdvAutonomous': True

See :ref:`radvd__ref_interfaces` for information about interface configuration.


Example inventory
-----------------

To enable :command:`radvd` configuration on a host, it needs to be added to the
``[debops_service_radvd]`` Ansible inventory group:

.. code-block:: none

   [debops_service_radvd]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses ``debops.radvd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/radvd.yml
   :language: yaml
