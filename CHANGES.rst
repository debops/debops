Changelog
=========

v0.1.4
------

*Released: 2016-06-30*

- Add support for GitLab 8.9. [gomez]

- Set the default GitLab version to '8.9'. [drybjed]

v0.1.3
------

*Released: 2016-06-30*

- Add support for GitLab 8.6. [gomez]

- Add support for gitlab 8.7. [benalbrecht]

- Add support for gitlab 8.8. [gomez]

- Reload ``systemd`` daemons on init script change. [drybjed]

v0.1.2
------

*Released: 2016-03-02*

- Add support for GitLab 8.1 [gomez]

- Add support for GitLab 8.5 [benalbrecht]

v0.1.1
------

*Released: 2015-10-13*

- Migration to debops.mariadb role. [scibi]
  If you have exisitng setup you have to:
  - move some files in secrets directory:
    ``secret/credentials/[GitLab FQDN]/mysql/root/password`` to ``secret/credentials/[GitLab FQDN]/mariadb/localhost/root/password``
    ``secret/credentials/[GitLab FQDN]/mysql/git/password`` to ``secret/mariadb/[GitLab FQDN]/credentials/gitlab/password``
  - set ``mariadb_server_flavor`` to ``mysql``


v0.1.0
------

*Released: 2015-09-29*

- Add Changelog. [drybjed]

- Add support for GitLab 7.10.

  Template of ``gitlab.yml`` configuration file is updated to GitLab 7.10.

  Variable ``gitlab_email_name`` is renamed to ``gitlab_email_display_name``.

  Removed ``gitlab_email_support``, ``gitlab_signup_enabled`` and
  ``gitlab_default_projects_limit`` variables.

  Added ``gitlab_email_reply_to`` variable.

  Install ``libkrb5-dev`` package before GitLab CE installation (required on
  Debian Jessie). [drybjed]

- Add support for GitLab 7.11. [drybjed]

- Added support for Gitlab LDAP Authentication. [xorgic]

- Add support for GitLab 7.12. [gomez]

- Add support for GitLab 7.13 and 7.14. [scibi]

- Create LDAP accout for gitlab user. [scibi]

- Add support for GitLab 8.0. [scibi]
