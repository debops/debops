Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

With the default configuration, ``debops.mosquitto`` role will configure
Mosquitto with a TLS listener accepting connections from any host (if the
:ref:`debops.pki` environment is detected), and plaintext listener accepting
connections only from localhost. Anonymous access to the broker will be
allowed.

By default, plaintext connections are not allowed over the network. You can
change that by setting the :envvar:`mosquitto__allow` variable with a list of
IP addresses or CIDR subnets to allow plaintext connections.


WebSocket configuration
-----------------------

WebSocket support will be enabled if a sufficient version of the
``libwebsockets`` library is detected; this was tested and works on Debian
Stretch; using upstream Mosquitto on older OS releases is not enough, and at
the time the role was written upstream Stretch version was not available. The
WebSocket listener will be configured for ``localhost`` connections only.

The role provides two playbooks, a "plain" and "nginx" version (see below). The
"nginx" playbook can be used to configure an :command:`nginx` reverse proxy for
the WebSocket listener. By default any host will be able to access the
WebSocket connection, this can be controlled separately from the normal TLS
connection using :envvar:`mosquitto__websockets_allow` variable.

You can test support for WebSockets in Mosquitto using:
http://www.hivemq.com/blog/full-featured-mqtt-client-browser


User accounts, ACL, password creation
-------------------------------------

For better security, you should configure some user accounts (see
:ref:`mosquitto__ref_auth_users`) and ACL entries for the broker. When user
accounts are defined, the role will automatically block the anonymous access;
this can be controlled using the :envvar:`mosquitto__allow_anonymous` variable.

The older Mosquitto releases (pre 1.4+) provide a :command:`mosquitto_passwd`
command which does not support batch password creation, therefore the role will
not configure the user accounts if such version is detected. You should either
enable upstream release (on older OS releases) or use Debian Stretch+ which
supports batch password creation.


.. _mosquitto__ref_avahi_support:

Avahi CNAME (alias) support
---------------------------

If the Avahi support managed by the ``debops.avahi`` Ansible role is detected,
the ``debops.mosquitto`` role will automatically create Avahi service entries
for the configured listeners. The Avahi configuration is managed by the
``avahi_*`` parameters in the listener configuration, see
:ref:`mosquitto__ref_listeners` for more details.


Example inventory
-----------------

The ``debops.mosquitto`` role needs to be enabled to be used in the DebOps
playbook. To do that, add the hosts that you want to configure Avahi on to the
``[debops_service_mosquitto]`` Ansible inventory group:

.. code-block:: none

   [debops_service_mosquitto]
   hostname

If you want to enable the :command:`nginx` reverse proxy on a given host for
WebSocket support, you can add that host to the
``[debops_service_mosquitto_nginx]`` Ansible inventory group:

.. code-block:: none

   [debops_service_mosquitto_nginx]
   hostname


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.mosquitto`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/mosquitto-plain.yml
   :language: yaml

There is a separate playbook for a Mosquitto instance with :command:`nginx`
used as a reverse proxy for WebSocket connections:

.. literalinclude:: ../../../../ansible/playbooks/service/mosquitto-nginx.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::mosquitto``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::mosquitto:acl``
  Tasks related to ACL configuration.

``role::mosquitto:passwd``
  Tasks related to user/password management.

``role::mosquitto:avahi``
  Tasks related to Avahi service support.

``role::mosquitto:config``
  Tasks related to global configuration.

``role::mosquitto:listeners``
  Tasks related to :command:`mosquitto` listener configuration.

``role::mosquitto:bridges``
  Tasks which configure MQTT bridge connections.
