Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

To manage Nginx on a given host or set of hosts, they need to be added
to the ``[debops_service_nginx]`` Ansible group in the inventory:

.. code:: ini

   [debops_service_nginx]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.nginx`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/nginx.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::nginx``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::nginx``
  Execute all ``debops.nginx`` role dependencies in its context.

``depend::secret:nginx``
  Run :ref:`debops.secret` dependent role in ``debops.nginx`` context.

``depend::apt_preferences:nginx``
  Run :ref:`debops.apt_preferences` dependent role in ``debops.nginx`` context.

``depend::ferm:nginx``
  Run :ref:`debops.ferm` dependent role in ``debops.nginx`` context.

``role::nginx:servers``
  Configure nginx servers configuration as configured by the ``nginx_servers``
  variable.
