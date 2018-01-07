Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

The ``debops.root_account`` role is included by default in the
:file:`common.yml` DebOps playbook; you don't need to do anything to have it
executed.

If you don’t want to let ``debops.root_account`` manage the root account, you
can do this with the following setting in your inventory:

.. code-block:: yaml

   root_account__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.root_account`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/root_account.yml
   :language: yaml
