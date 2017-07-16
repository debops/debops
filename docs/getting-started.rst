.. include:: includes/all.rst

.. contents::
   :local:


Upstream package is used by default
-----------------------------------

Text...


Auth is insecure by default
------------------------------------

The auth service....


Standalone deployment or cluster
--------------------------------

With the default configuration, the ``debops.auth`` role will deploy
the auth service in a "standalone" mode without exposing the service
to the outside world. This allows easy deployments for development or testing
purposes....


Use as a role dependency
------------------------

Text...


Example inventory
-----------------

To deploy auth in a standalone mode, you can add the host to the
``[debops_service_auth]`` Ansible inventory group:

.. code-block:: none

   [debops_service_auth]
   hostname

The default playbook supports use of different Ansible inventory groups for
different types of Elasticsearch nodes.
See :ref:`auth__ref_clustering` for more details.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.auth`` role:

.. literalinclude:: playbooks/auth.yml
   :language: yaml


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::auth``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::auth:config``
  Generate the auth configuration taking into account different
  configuration sources.
