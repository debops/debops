Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

``debops.users`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

If you don’t want to let ``debops.users`` manage user accounts, you can disable
it with the following setting in your inventory:

.. code-block:: yaml

   users__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.users`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/users.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::users``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
