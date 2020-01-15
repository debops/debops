Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.libuser`` Ansible role is included by default in the
:file:`common.yml` DebOps playbook; you don't need to do anything to have it
executed. It's also included in the :file:`bootstrap.yml` and the
:file:bootstrap-ldap.yml` playbooks to help create the local sysadmin accounts
during host bootstrapping.

If you don’t want to let ``debops.libuser`` manage user accounts, you can
disable it with the following setting in your inventory:

.. code-block:: yaml

   libuser__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.libuser`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/libuser.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Common role tags:

``role::libuser``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::libuser``
  Main role tag, should be used in the playbook to skip all of the role tasks.
