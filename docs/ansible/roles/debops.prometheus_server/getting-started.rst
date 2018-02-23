Getting started
===============

.. contents::
   :local:


Default configuration
---------------------

Access from the net
+++++++++++++++++++

By default prometheus server only listen on `localhost:9090` this can be changed by the follow variables.

:envvar:`prometheus_server__nginx`

Enables an nginx proxy under the domain ::envvar:prometheus_server__domain .
For secure communication base_auth is active by default.

:envvar:`prometheus_server__accept_any`

Enables direct tcp connection to the prometheus_server on port 9090.
All connections are allowed

:envvar:`prometheus_server__allow`

Allows a list of CIDR subnets access via tcp port 9090

Add metric targets
++++++++++++++++++

Default metric getter are :envvar:`prometheus_server__default_jobs`.

More can be added through the variables `prometheus_server__*_jobs` see default variables `Prometheus Server Configuration`.

Example inventory
-----------------

To enable Prosody server support on a host, it needs to be included in the Ansible inventory in a specific group:

.. code-block:: none

   [debops_service_prometheus_server]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.prometheus_server`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/prometheus_server.yml
   :language: yaml

Example depended
----------------

.. code-block:: none

  ...
  roles:
    - role: debops.prometheus_server
      prometheus_server__dependent_jobs: ':envvar:`prometheus_server__default_jobs`'
      tags: [ 'role::prometheus' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::prometheus_server``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
``role::ferm``
  Role tag for configure the firewall ferm.
