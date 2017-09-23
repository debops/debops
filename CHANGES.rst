.. _gitlab__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.gitlab**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.gitlab master`_ - unreleased
------------------------------------

.. _debops.gitlab master: https://github.com/debops/ansible-gitlab/compare/v0.2.2...master

Removed
~~~~~~~

- Remove support for MySQL / MariaDB. If you used it, you must migrate the database:
  https://github.com/gitlabhq/gitlab-recipes/tree/master/database/migrate-mysql-to-postgres
  [bfabio_]


`debops.gitlab v0.2.2`_ - 2017-08-16
------------------------------------

.. _debops.gitlab v0.2.2: https://github.com/debops/ansible-gitlab/compare/v0.2.1...v0.2.2

Added
~~~~~

- Add support for connecting GitLab to Piwik Analytics. [jpeeters]

- Add the ``libre2-dev`` APT package to required dependencies. [drybjed_]

- Add support for GitLab 9.4. [drybjed_]

Changed
~~~~~~~

- Compile required Go binaries in :command:`gitlab-shell` installation.
  [drybjed_]

- Stop and start running :command:`gitaly` service during an upgrade because
  the binary cannot be replaced without errors. Small bugs related to
  :command:`gitaly` service have been fixed. [drybjed_]


`debops.gitlab v0.2.1`_ - 2017-07-26
------------------------------------

.. _debops.gitlab v0.2.1: https://github.com/debops/ansible-gitlab/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Role documentation improvements. [ypid_]

- Add PATH environment for gitlab-workhorse service for artifact uploads. [cultcom]

- Add support for debian 'stretch'. [cultcom]

- Fix base packages installation for 'stretch'. [cultcom]

- Cleanup and simplify gitlab-workhorse service file.
  Standard input and output redirection does not work within systemd. [cultcom]

- Add support for GitLab 9.0, 9.1, 9.2 and 9.3. [bfabio_] [cultcom]

- Always create 'pages' directory for "rake backup" to succeed. [cultcom]


`debops.gitlab v0.2.0`_ - 2017-04-06
------------------------------------

.. _debops.gitlab v0.2.0: https://github.com/debops/ansible-gitlab/compare/v0.1.8...v0.2.0

Changed
~~~~~~~

- Change the installation procedure with a PostgreSQL database. The
  ``gitlab:setup`` Rake task drops the database, so instead the role runs the
  specific Rake tasks that install the schema and configure PostgreSQL database
  directly. This change should not affect existing installations. [drybjed_]

- Configuration of the ``pg_trgm`` PostgreSQL extension has been moved from the
  ``debops.gitlab`` role to dependent variables of the debops.postgresql_ role.
  [drybjed_]

- Variables in the :file:`vars/main.yml` file have been moved to the
  :file:`defaults/main.yml` file to allow their modification via Ansible inventory.
  [drybjed_]

- Configuration for other Ansible roles passed as role dependent variables has
  been moved to the :file:`defaults/main.yml` for easier management. [drybjed_]

- The configuration of the PostgreSQL database and roles has changed. The
  database will now be owned by a role of the same name (by default
  ``gitlabhq_production``) which cannot login to the server directly. The
  ``gitlab`` PostgreSQL role will belong to the ``gitlabhq_production``
  PostgreSQL group and should have access to the database.

  This change will be applied in the existing installations, but it shouldn't
  impact the service. [drybjed_]

- Rename the ``gitlab_database`` variable to :envvar:`gitlab__database` to
  allow switch to the Ansible playbook-based role dependencies. **If you
  configured the GitLab database in the inventory, you will need to update the
  inventory before applying the new role; otherwise the application will
  break.** [drybjed_]

- The role dependencies have been moved to the playbook. The ``debops.gitlab``
  role will now check if a suitable SQL database is available on the host
  before installing GitLab. If you are using a remote SQL database, you should
  check it's corresponding client role to prepare correct Ansible local facts.
  [drybjed_]

- The ``debops.gitlab`` role will check if PostgreSQL or MariaDB role facts are
  present on a host and will choose the installed database automatically. The
  PostgreSQL database is preferred to keep upstream preference.

  The selected SQL database is remembered in Ansible local facts. On existing
  installations this might result in a broken installation where a PostgreSQL
  database is detected without a corresponding fact pointing to a MariaDB
  database. In this case users should enforce the GitLab database choice
  through Ansible inventory. [drybjed_]


`debops.gitlab v0.1.8`_ - 2017-03-12
------------------------------------

.. _debops.gitlab v0.1.8: https://github.com/debops/ansible-gitlab/compare/v0.1.7...v0.1.8

Added
~~~~~

- Add support for GitLab 8.15. [Oldkarkass]

- Add support for GitLab 8.16. [cultcom]

- Add support for GitLab 8.17. [bfabio]

- Add support for GitLab services managed by :command:`systemd` units in
  a separate slice instead of the upstream SysVinit script. The role should
  preserve the current service management method on already installed
  instances; new :command:`systemd` support will be enabled only on new
  installs on hosts that use :command:`systemd` as the service manager.
  [cultcom, drybjed_]

- Add support for GitLab Pages. It will be enabled on GitLab 8.17+, as long as
  a suitable domain is configured in the ``gitlab_pages_domain`` variable.
  [bfabio]

Changed
~~~~~~~

- Update :file:`gitlab.yml` configuration file template. [Oldkarkass]


`debops.gitlab v0.1.7`_ - 2016-11-18
------------------------------------

.. _debops.gitlab v0.1.7: https://github.com/debops/ansible-gitlab/compare/v0.1.6...v0.1.7

Changed
~~~~~~~

- Update the ``ldap_entry`` task to use new ``attributes`` parameter added to
  the newest module version. [drybjed_]

Fixed
~~~~~

- Fix an issue on Ansible v2.2 where dictionary keys in skipped tasks are
  undefined. [drybjed_]


`debops.gitlab v0.1.6`_ - 2016-10-22
------------------------------------

.. _debops.gitlab v0.1.6: https://github.com/debops/ansible-gitlab/compare/v0.1.5...v0.1.6

Added
~~~~~

- Add support for GitLab 8.12. [bfabio]

- Add support for GitLab 8.13. [drybjed_]

Changed
~~~~~~~

- Switch from installing Go support in the role to using the debops.golang_
  role which will provide support for Go 1.6. [bfabio]


`debops.gitlab v0.1.5`_ - 2016-09-08
------------------------------------

.. _debops.gitlab v0.1.5: https://github.com/debops/ansible-gitlab/compare/v0.1.4...v0.1.5

Changed
~~~~~~~

- Update documentation and Changelog. [drybjed_]

- The ``debops.gitlab`` role now requies at least Ansible 2.1 due to the
  requirements of the LDAP modules used by the role. [drybjed_]

- Update the Redis support to automatically configure password authentication
  used by the debops.redis_ Ansible role. [drybjed_]

- Ensure that debops.ruby_ role installs packages required to build native gem
  extensions. [drybjed_]

- Add path for GitLab build artifacts and ensure that all required directories
  exist. [drybjed_]

- Ensure that ``gitlab-shell`` is checked out on first install even when the
  latest tag and the main ``master`` branch are the same. [drybjed_]

- Fix Ansible warnings about :command:`sudo` and :command:`git` modules. [drybjed_]

Removed
~~~~~~~

- Remove an unused task with a variable register. [drybjed_]


`debops.gitlab v0.1.4`_ - 2016-06-30
------------------------------------

.. _debops.gitlab v0.1.4: https://github.com/debops/ansible-gitlab/compare/v0.1.3...v0.1.4

Added
~~~~~

- Add support for GitLab 8.9. [gomez]

Changed
~~~~~~~

- Set the default GitLab version to ``8.9``. [drybjed_]


`debops.gitlab v0.1.3`_ - 2016-06-30
------------------------------------

.. _debops.gitlab v0.1.3: https://github.com/debops/ansible-gitlab/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add support for GitLab 8.6. [gomez]

- Add support for gitlab 8.7. [benalbrecht]

- Add support for gitlab 8.8. [gomez]

Changed
~~~~~~~

- Reload ``systemd`` daemons on init script change. [drybjed_]


`debops.gitlab v0.1.2`_ - 2016-03-02
------------------------------------

.. _debops.gitlab v0.1.2: https://github.com/debops/ansible-gitlab/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add support for GitLab 8.1 [gomez]

- Add support for GitLab 8.5 [benalbrecht]


`debops.gitlab v0.1.1`_ - 2015-10-13
------------------------------------

.. _debops.gitlab v0.1.1: https://github.com/debops/ansible-gitlab/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Migration to debops.mariadb_ role. [scibi_]
  If you have exisitng setup you have to move some files in secrets directory:

  .. code-block:: none

     secret/credentials/[GitLab FQDN]/mysql/root/password -> secret/credentials/[GitLab FQDN]/mariadb/localhost/root/password
     secret/credentials/[GitLab FQDN]/mysql/git/password -> secret/mariadb/[GitLab FQDN]/credentials/gitlab/password

  And set ``mariadb_server_flavor`` to :command:`mysql`.


debops.gitlab v0.1.0 - 2015-09-29
---------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Add support for GitLab 7.10.

  Template of :file:`gitlab.yml` configuration file is updated to GitLab 7.10.

  Variable ``gitlab_email_name`` is renamed to ``gitlab_email_display_name``.

  Removed ``gitlab_email_support``, ``gitlab_signup_enabled`` and
  ``gitlab_default_projects_limit`` variables.

  Added ``gitlab_email_reply_to`` variable.

  Install ``libkrb5-dev`` package before GitLab CE installation (required on
  Debian Jessie). [drybjed_]

- Add support for GitLab 7.11. [drybjed_]

- Added support for Gitlab LDAP Authentication. [xorgic]

- Add support for GitLab 7.12. [gomez]

- Add support for GitLab 7.13 and 7.14. [scibi_]

- Add support for GitLab 8.0. [scibi_]

Changed
~~~~~~~

- Create LDAP account for gitlab user. [scibi_]
