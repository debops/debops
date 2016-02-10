Getting started
===============

.. contents::
   :local:

Initial configuration
---------------------

``debops.contrib-etckeeper`` will install the ``etckeeper`` Debian package
which will hook into the package management and from now on automatically
commit changes to a local git repository under :file:`/etc/.git`.

By default :command:`git` is used as VCS. This can be changed by inventory
variables.

Example inventory
-----------------

.. code:: YAML

   ## If you don’t what to track hashed passwords.
   etckeeper_gitignore_group:
     - 'shadow'
     - 'shadow-'

In Ansible's inventory.

Example playbook
----------------

Here's an example playbook that can be used to enable and manage the :program:`atd`
service on a set of hosts:

.. code:: YAML

   ---
   - name: Put /etc under version control using etckeeper
     hosts: debops_all_hosts
     become: True

     roles:

       - role: debops.contrib-etckeeper
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
