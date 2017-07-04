Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst


Example inventory
-----------------

To configure RabbitMQ on a host, it should be added to the
``[debops_service_rabbitmq_server]`` Ansible inventory group:

.. code-block:: none

   [debops_service_rabbitmq_server]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.rabbitmq_server`` role:

.. literalinclude:: playbooks/rabbitmq_server.yml
   :language: yaml
