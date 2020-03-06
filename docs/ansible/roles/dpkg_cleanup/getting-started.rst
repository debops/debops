.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Example inventory
-----------------

The :ref:`debops.dpkg_cleanup` role is not designed to be used directly. It
should be imported into other Ansible roles with custom configuration for each
(see below). Alternatively, it can be included in the playbooks of other
Ansible roles.


Example playbook
----------------

The :ref:`debops.dpkg_cleanup` role does not have it's own playbook. The role
is designed to be used by other Ansible roles via the ``import_role`` Ansible
module, usually at the end of the task list of a given role.

In the :file:`defaults/main.yml` file of the example ``application`` role, add:

.. code-block:: yaml

   application__dpkg_cleanup__dependent_packages:
     - name: 'application'
       remove_files:
         - '/path/to/custom/file'
         - '/path/to/other/file'
       restart_services:
         - 'other-service'

In the :file:`tasks/main.yml` file of the ``application`` role, add:

.. code-block:: yaml

   - import_role:
       name: 'dpkg_cleanup'
     vars:
       dpkg_cleanup__dependent_packages:
         - '{{ application__dpkg_cleanup__dependent_packages }}'
     when: application__deploy_state != 'absent'
     tags: [ 'role::dpkg_cleanup', 'skip::dpkg_cleanup',
             'role::application:dpkg_cleanup' ]

This configuration will ensure that the users can modify the list of files or
directories to manipulate through the Ansible inventory, if necessary.

.. warning:: Keep in mind that if the :ref:`debops.dpkg_cleanup` role is used
   via the ``import_role`` Ansible module in multiple roles, due to the
   behaviour of this Ansible module each such instance needs to have its own
   :envvar:`dpkg_cleanup__dependent_packages` variable definition. Otherwise
   the last instance of the role preprocessed by Ansible will define this
   variable for each instance without it.
