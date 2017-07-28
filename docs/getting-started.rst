Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:
   :depth: 1

Support for Unbound DNS resolver
--------------------------------

The ``debops.opendkim`` role checks if the Unbound service has been installed
on a given host, by checking for the Ansible local facts defined by the
``debops.unbound`` role. If Unbound is present, OpenDKIM will automatically use
it to resolve DNS queries and check DNSSEC validity.


Example inventory
-----------------

The install and configure OpenDKIM on a host, it needs to be present in the
``[debops_service_opendkim]`` Ansible inventory group:

.. code-block:: none

   [debops_service_opendkim]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.opendkim`` role:

.. literalinclude:: playbooks/opendkim.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::opendkim``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
