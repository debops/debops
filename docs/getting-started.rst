Getting started
===============

.. contents::
   :local:


Example inventory
-----------------

``debops.apt`` is included by default in the :file:`common.yml` DebOps playbook;
you don't need to do anything to have it executed.

If you don’t want to let ``debops.apt`` manage APT, you can do this with the
following setting in your inventory::

   apt__enabled: False

Example playbook
----------------

Here's an example playbook for using the role without the DebOps playbook::

    ---
    - name: Configure and manage APT Package Manager
      hosts: [ 'debops_all_hosts', '!debops_no_common' ]
      become: True

      roles:

        - role: debops.apt_preferences
          tags: [ 'role::apt_preferences' ]
          apt_preferences__dependent_list:
            - '{{ apt__apt_preferences__dependent_list }}'

        - role: debops.apt
          tags: [ 'role::apt' ]


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::apt``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::apt:install``
  Tasks related to package installation.
