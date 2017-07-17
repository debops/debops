Getting started
===============

Default configuration
---------------------

The ``debops.postfix`` role configures a basic Postfix SMTP server with
configuration similar to the "Internet Site" configuration enabled by default
by the Debian package. Additional configuration is defined in separate
variables and can be easily disabled or modified if necessary.

The Postfix service will be configured to use TLS connections and strong
encryption by default. This might interfere with SMTP service operation for
older installations that don't support required features.


Example inventory
-----------------

The install and configure Postfix on a host, it needs to be present in the
``[debops_service_postfix]`` Ansible inventory group:

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
