Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

By default :command:`git` is used as VCS. This can be changed by the inventory
variables ``etckeeper__vcs``.

Example inventory
-----------------

.. code:: YAML

   ## If you don’t what to track hashed passwords.
   etckeeper__gitignore_group:
     - 'shadow'
     - 'shadow-'

In Ansible's inventory.

Example playbook
----------------

Here's an example playbook that can be used to put :file:`/etc` under version
control using :program:`etckeeper` on a set of hosts:

.. code:: YAML

   ---
   - name: Put /etc under version control using etckeeper
     hosts: 'debops_service_etckeeper'
     become: True

     roles:

       - role: debops-contrib.etckeeper
         tags: [ 'role::etckeeper' ]

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::etckeeper``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::etckeeper:vcs_config``
  Run tasks related to configuring VCS options.
