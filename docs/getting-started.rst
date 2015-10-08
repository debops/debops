Getting started
===============

.. contents::
   :local:


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::etherpad``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``type::dependency``
  This tag specifies which tasks are defined in role dependencies. You can use
  this to omit them using ``--skip-tags`` parameter.

``depend-of::etherpad``
  Execute all ``debops.etherpad`` role dependencies in its context.

``depend::etc_services:etherpad``
  Run ``debops.etc_services`` dependent role in ``debops.etherpad`` context.

``depend::nodejs:etherpad``
  Run ``debops.nodejs`` dependent role in ``debops.etherpad`` context.

``depend::mariadb:etherpad``
  Run ``debops.mariadb`` dependent role in ``debops.etherpad`` context.

``depend::nginx:etherpad``
  Run ``debops.nginx`` dependent role in ``debops.etherpad`` context.

``role::etherpad:source``
  Run tasks related to install Etherpad from source.

``role::etherpad:config``
  Run tasks related to configuring Etherpad.

``role::etherpad:plugins``
  Run tasks which install the defined Etherpad plugins.

``role::etherpad:api:call``
  Run tasks API call tasks. Can be used for rapid API calls.

``role::etherpad:api``
  Same as ``role::etherpad:api:call`` but ensures that the service is running
  and waiting for it to start before trying.

