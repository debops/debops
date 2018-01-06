Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To host the DebOps API, add the hosts to the
``debops_service_debops_api`` Ansible inventory host group:

.. code:: ini

   [debops_service_debops_api]
   hostname

Example playbook
----------------

Here's an example playbook that can be used to host the DebOps API on a set of
hosts:

.. literalinclude:: ../../../../ansible/playbooks/service/debops_api.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::debops_api``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::debops_api:pkg``
  Tasks related to system package management like installing, upgrading or
  removing packages.

``role::debops_api:git``
  Tasks related to ``git`` operations. Especially the tasks "DebOps API input
  data" can take up to one minute so you might want to skip them on subsequent
  role runs.

``role::debops_api:cron``
  Tasks related to ``cron`` job configuration.
