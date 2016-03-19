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
