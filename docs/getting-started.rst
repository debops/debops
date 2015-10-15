Getting started
===============

.. contents::
   :local:

APT preferences configuration
-----------------------------

You can use this role to select different version of APT packages available
without specifying the version directly in the playbooks or roles. This helps
to ensure that APT dependency tree is stable and there are no conflicts between
different versions.

Example inventory
-----------------

``debops.apt_preferences`` role is included in the ``common.yml`` playbook, you
can add your own entries in Ansible inventory and they should be picked up
automatically on the next playbook run.

Example playbook
----------------

Here's an example playbook that can be used to manage APT preferences. It will
make sure that on Debian Wheezy system will prefer ``nginx`` packages from
Wheezy Backports repository::

    ---
    - hosts: debops_apt_preferences
      become: True

      roles:

        - role: debops.apt_preferences
          apt_preferences_dependent_list:

            - package: 'nginx nginx-*'
              backports: [ 'wheezy' ]
              reason: 'Support for SPDY protocol'

