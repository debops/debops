Changelog
=========

v0.2.0
------

*Unreleased*

- Renamed ``etherpad_mysql_database_password`` to
  ``etherpad_database_password`` and changed path where the password is saved
  on the Ansible controller for consistory reasons. Note that this will create a new database user password and configure it!
  Please move the old password file under ``"credentials/" + ansible_fqdn + "/mysql/" + etherpad_database_config[etherpad_database].username + "/password``
  to ``'mariadb/' + ansible_local.mariadb.delegate_to + '/credentials/' + librenms_database_user + '/password'``. [ypid]

- Changed ``etherpad_home`` from ``/srv/users/{{ etherpad_user }}`` to ``{{
  ansible_local.root.app + "/" + etherpad_user`` consistory reasons. [ypid]

