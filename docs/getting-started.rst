Getting started
===============

.. include:: includes/all.rst

.. contents::
   :local:

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
  Run debops.secret_ dependent role in ``debops.nginx`` context.

``depend::apt_preferences:nginx``
  Run debops.apt_preferences_ dependent role in ``debops.nginx`` context.

``depend::ferm:nginx``
  Run debops.ferm_ dependent role in ``debops.nginx`` context.

``role::nginx:servers``
  Configure nginx servers configuration as configured by the ``nginx_servers``
  variable.
