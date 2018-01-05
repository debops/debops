Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

``debops.cron`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

If you don’t want to let ``debops.cron`` manage the :program:`cron` jobs, you
can do this with the following setting in your inventory:

.. code-block:: yaml

   cron__enabled: False


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.cron`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/cron.yml
   :language: yaml
