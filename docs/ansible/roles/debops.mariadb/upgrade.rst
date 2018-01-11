.. _mariadb__ref_upgrade_notes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
changelog for more details about what has changed.


From v0.2.2 to v0.3.0
---------------------

Due to the new definition of :envvar:`mariadb__delegate_to` all users of the
role are impacted under the following conditions:

- The Ansible inventory name is different from the FQDN for the hosts where
  this role is applied to.

  **AND**

- For the those hosts the :envvar:`mariadb__server` variable is not defined
  in the Ansible inventory which means the default value is used during role
  execution.

  **AND**

- For those hosts the :envvar:`mariadb__delegate_to` variable is not defined
  in the Ansible inventory which means the default value is used during role
  execution.

The first time the new version of the role is run standalone and/or as a
dependency of Ansible roles every user account defined through
:envvar:`mariadb__users`, :envvar:`mariadb__dependent_users` or
``mariadb_users`` will change its secrets path which will regenerate
the database user password. **This may result in an inaccessible database in
case those passwords are also used externally.** Ansible roles which are
accessing the ``delegate_to`` value through the local facts (usually to access
the password via secrets lookup) will automatically learn the new path and don't
need to be changed. Mechanisms which get the password via manually defined
secrets path MUST be updated accordingly.

This impact can be avoided by manually adding the following definition to the
Ansible inventory of the affected hosts:

.. code-block:: yaml

   mariadb__delegate_to: '{{ ansible_fqdn }}'
