Getting started
===============

.. contents:: Sections
   :local:


Example inventory
-----------------

To enable GitLab service on a host, it needs to be included in the
``[debops_service_gitlab]`` Ansible inventory group:

.. code-block:: none

   [debops_service_gitlab]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.gitlab`` role:

.. literalinclude:: playbooks/gitlab.yml
   :language: yaml
