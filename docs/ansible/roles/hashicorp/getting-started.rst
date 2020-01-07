Getting started
===============

.. include:: ../../../includes/global.rst

.. contents::
   :local:


Initial configuration
---------------------

The ``debops.hashicorp`` role does not install any HashiCorp_ applications by
default, even if enabled in the Ansible inventory. You need to specify the
application names you wish to install using the :envvar:`hashicorp__applications`
list. For example, to install ``consul`` on all hosts that use the role, create
a file in the Ansible inventory with contents:

.. code-block:: yaml

   hashicorp__applications: [ 'consul' ]

The role will install the ``consul`` binary, after verifying its authenticity,
in the :file:`/usr/local/bin` directory so that it will be automatically available
for all users.

List of HashiCorp_ applications supported by the role can be found in the
:envvar:`hashicorp__default_version_map` default variable. You can also use it to
easily install all supported applications at once:

.. code-block:: yaml

   hashicorp__applications: '{{ hashicorp__default_version_map.keys() }}'

After the binaries are installed, they are ready to be configured by other
Ansible roles. See the :ref:`hashicorp__ref_ansible_integration` document for
more details.


Example inventory
-----------------

The ``debops.hashicorp`` Ansible role is not enabled by default. To enable it
on a host, you need to include that host in the ``[debops_service_hashicorp]``
inventory group:

.. code-block:: none

   [debops_service_hashicorp]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.hashicorp`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/hashicorp.yml
   :language: yaml
