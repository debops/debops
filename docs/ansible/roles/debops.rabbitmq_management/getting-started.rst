Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

The role will detect if an existing installation of RabbitMQ done by the
:ref:`debops.rabbitmq_server` role is present on a host. If it's found, the
Management Console will be configured locally. Otherwise, no RabbitMQ
configuration will take place, but role will still install the :command:`nginx`
server on a host and configure a reverse proxy instance. In that case, you
might want to modify the :envvar:`rabbitmq_management__app_host`,
:envvar:`rabbitmq_management__app_port` and
:envvar:`rabbitmq_management__app_protocol` parameters to point to a remote
RabbitMQ Management Console instance.


Example inventory
-----------------

To configure RabbitMQ Management Console on a host, it should be added to the
``[debops_service_rabbitmq_management]`` Ansible inventory group:

.. code-block:: none

   [debops_service_rabbitmq_management]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.rabbitmq_management`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/rabbitmq_management.yml
   :language: yaml
