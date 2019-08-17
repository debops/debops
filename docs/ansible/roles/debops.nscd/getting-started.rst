Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To enable the :command:`nscd` service on a host, you need to add it to the
``[debops_service_nscd]`` Ansible inventory group.

.. code-block:: none

   [debops_service_nscd]
   hostname

A common case is configuration of LDAP authentication in the entire cluster of
hosts. You can enable :command:`debops.nscd` role on all DebOps hosts in the
Ansible inventory at once:

.. code-block:: none

   [debops_all_hosts]
   hostname1
   hostname2

   [debops_service_nscd:children]
   debops_all_hosts

The :command:`nscd` service can also be installed and configured by other
playbooks, for example ``bootstrap-ldap.yml``. In such cases the custom
playbook will configure the :command:`nscd` service on a host, but the role
playbook will not work on a host automatically; you will have to include that
host in the ``[debops_service_nscd]`` Ansible inventory group via one of the
methods above to be able to change the service configuration.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nscd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nscd.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::nscd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.nscd`` Ansible role:

- Manual pages: :man:`nscd.conf(5)`
