Getting started
===============

Example inventory
-----------------

To run this role on servers, they should be included
in the ``[debops_service_postfix]`` Ansible group:

.. code-block:: none

   [debops_service_postfix]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.postfix`` role:

.. literalinclude:: playbooks/postfix.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::postfix``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::postfix``
  Execute all ``debops.postfix`` role dependencies in its context.

``depend::ferm:postfix``
  Run ``debops.ferm`` dependent role in ``debops.postfix`` context.
