.. _gitlab__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.gitlab**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.gitlab master`_ - unreleased
------------------------------------

.. _debops.gitlab master: https://github.com/debops/ansible-gitlab/compare/v0.1.6...master


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

- Fix Ansible warnings about ``sudo`` and ``git`` modules. [drybjed_]

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

- Migration to debops.mariadb_ role. [scibi]
  If you have exisitng setup you have to:
  - move some files in secrets directory:
    ``secret/credentials/[GitLab FQDN]/mysql/root/password`` to ``secret/credentials/[GitLab FQDN]/mariadb/localhost/root/password``
    ``secret/credentials/[GitLab FQDN]/mysql/git/password`` to ``secret/mariadb/[GitLab FQDN]/credentials/gitlab/password``
  - set ``mariadb_server_flavor`` to ``mysql``


debops.gitlab v0.1.0 - 2015-09-29
---------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Add support for GitLab 7.10.

  Template of ``gitlab.yml`` configuration file is updated to GitLab 7.10.

  Variable ``gitlab_email_name`` is renamed to ``gitlab_email_display_name``.

  Removed ``gitlab_email_support``, ``gitlab_signup_enabled`` and
  ``gitlab_default_projects_limit`` variables.

  Added ``gitlab_email_reply_to`` variable.

  Install ``libkrb5-dev`` package before GitLab CE installation (required on
  Debian Jessie). [drybjed_]

- Add support for GitLab 7.11. [drybjed_]

- Added support for Gitlab LDAP Authentication. [xorgic]

- Add support for GitLab 7.12. [gomez]

- Add support for GitLab 7.13 and 7.14. [scibi]

- Add support for GitLab 8.0. [scibi]

Changed
~~~~~~~

- Create LDAP accout for gitlab user. [scibi]
