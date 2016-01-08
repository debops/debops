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
