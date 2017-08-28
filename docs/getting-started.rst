.. _roundcube__ref_getting_started:

Getting started
===============

.. contents::
   :local:

.. include:: includes/all.rst


.. _roundcube__ref_default_setup:

Default setup
-------------

If you don't specify any configuration values, the role will setup a Nginx_
HTTP server running a default installation of the latest Roundcube stable
release which is then accessible via ``https://roundcube.<your-domain>``.
SQLite is used as database backend for storing the user settings.


.. _roundcube__ref_example_inventory:

Example inventory
-----------------

Roundcube can be installed on a given host by adding it to the
``[debops_service_roundcube]`` Ansible inventory group::

    [debops_service_roundcube]
    hostname


.. _roundcube__ref_example_playbook:

Example playbook
----------------

The following playbook can be used with DebOps. If you are using these role
without DebOps you might need to adapt them to make them work in your setup.

.. literalinclude:: playbooks/roundcube.yml
   :language: yaml

This playbook is also shipped with the role under :file:`docs/playbooks/`.


.. _roundcube__ref_ansible_tags:

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::roundcube``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::roundcube:pkg``
  Run tasks related to system package installation.

``role::roundcube:deployment``
  Run tasks related to the application deployment and update.

``role::roundcube:config``
  Run tasks related to the Roundcube application configuration.

``role::roundcube:database``
  Run tasks related to setup or update the database user and schema.
