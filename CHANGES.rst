Changelog
=========

.. include:: includes/all.rst

**debops.etherpad**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.etherpad master`_ - unreleased
--------------------------------------

.. _debops.etherpad master: https://github.com/debops/ansible-etherpad/compare/v0.1.0...master

Added
~~~~~

- Add support for running Etherpad via a :command:`systemd` service. [drybjed_]

Changed
~~~~~~~

- Renamed ``etherpad_mysql_database_password`` to
  ``etherpad_database_password`` and changed path where the password is saved
  on the Ansible controller for consistory reasons. Note that this will create a new database user password and configure it!
  Please move the old password file under ``"credentials/" + ansible_fqdn + "/mysql/" + etherpad_database_config[etherpad_database].username + "/password``
  to ``'mariadb/' + ansible_local.mariadb.delegate_to + '/' + ansible_local.mariadb.port + '/credentials/' + librenms_database_user + '/password'``. [ypid_]

- Changed ``etherpad_home`` from :file:`/srv/users/{{ etherpad_user }}` to ``{{
  ansible_local.root.app + "/" + etherpad_user`` consistory reasons. [ypid_]

- Role dependencies have been moved from :file:`meta/main.yml` file to a custom
  Ansible playbook. Configuration for these dependencies is now in default
  variables. [drybjed_]

- Updated documentation and Changelog. [drybjed_]

- Register the :command:`etherpad-lite` TCP port in :file:`/etc/services` using
  role dependent variables. [drybjed_]

- Configure log rotation through role dependent variables. [drybjed_]


debops.etherpad v0.1.0 - 2015-09-15
-----------------------------------

Added
~~~~~

- First release. [drybjed_]
