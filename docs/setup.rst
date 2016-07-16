DebOps API setup
================

.. contents::
   :local:

The setup requires https://github.com/debops/docs/ to be setup on the same host
as the scripts in debops/docs/ currently also generate the API data.

Example inventory
-----------------

To provide the DebOps API, add the hosts to the
``debops_internal_service_api`` Ansible inventory host group:

.. code:: ini

   [debops_internal_service_api]
   hostname

Example playbook
----------------

Here's an example playbook that can be used to setup the DebOps API on a set of
hosts:

.. literalinclude:: playbooks/api.yml
   :language: yaml
