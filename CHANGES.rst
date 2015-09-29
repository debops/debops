Changelog
=========

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
