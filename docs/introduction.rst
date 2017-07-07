Introduction
============

`RabbitMQ <https://www.rabbitmq.com/>`_ is an Open Source message broker which
supports AMQP, STOMP and MQTT protocols.

This ansible role can be used to enable and configure the
`RabbitMQ Management Console <https://www.rabbitmq.com/management.html>`_.
The role can configure the plugin in a locally installed RabbitMQ service, or
configure a reverse proxy to a remote instance of RabbitMQ.

See the ``debops.rabbitmq_server`` Ansible role for general RabbitMQ service
deployment and configuration.


Installation
~~~~~~~~~~~~

This role requires at least Ansible ``v2.3.0``. To install it, run:

.. code-block:: console

   ansible-galaxy install debops.rabbitmq_management


..
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
