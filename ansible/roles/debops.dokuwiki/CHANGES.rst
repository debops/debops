Changelog
=========

.. include:: includes/all.rst

**debops.dokuwiki**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.dokuwiki master`_ - unreleased
--------------------------------------

.. _debops.dokuwiki master: https://github.com/debops/ansible-environment/compare/v0.3.0...master


`debops.dokuwiki v0.3.0`_ - 2016-07-17
--------------------------------------

.. _debops.dokuwiki v0.3.0: https://github.com/debops/ansible-environment/compare/v0.2.0...v0.3.0

Added
~~~~~

- Add ``tag`` plugin with required ``pagelist`` plugin for page tagging
  support. [drybjed_]

- ``dokuwiki_plugins_enabled`` variable can be used to enable or disable custom
  plugin and template installation globally. [drybjed_]

- Add the ``rst`` DokuWiki plugin. [drybjed_]

Changed
~~~~~~~

- Remove hard role dependencies. Configuration of other roles is moved to
  :file:`defaults/main.yml` and updated playbook is added in the
  ``debops.dokuwiki`` documentation. Role now uses debops.php_ role instead
  of ``debops.php5`` to configure PHP support. [drybjed_]

- Update documentation and Changelog. [drybjed_]

- Remove ``no_log: True`` from tasks that clone different git repositories.
  [drybjed_]

- List of tasks in the role is reorganized and cleaned up. [drybjed_]

- Default list of DokuWiki plugins and templates are moved to separate
  variables, so that ``dokuwiki_plugins`` and ``dokuwiki_templates`` can be used
  in inventory. [drybjed_]

- The ``dokuwiki_main_domain`` variable is now a string instead of a list.
  [drybjed_]

- Rename all role variables from ``dokuwiki_*`` to ``dokuwiki__*`` to move them
  to their own namespace. [drybjed_]

Fixed
~~~~~

- Fix Ansible 2.1 deprecation warnings. [drybjed_]


`debops.dokuwiki v0.2.0`_ - 2015-09-03
--------------------------------------

.. _debops.dokuwiki v0.2.0: https://github.com/debops/ansible-environment/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add ``gallery`` DokuWiki plugin to list of default plugins. [drybjed_]

Changed
~~~~~~~

- Use a static, configurable filename for nginx configuration. This helps
  when wiki domain is changed on an existing installation.

  This change will generate a new nginx configuration file. Depending on your
  server layout you might need to remove at least the symlink to the old
  DokuWiki configuration file to prevent nginx server from failing to
  restart properly. [drybjed_]

- Change the ``dokuwiki`` system user home directory to be the same as website
  directory, based on ``ansible_local.nginx.www`` local Ansible fact. [drybjed_]

- Add missing ``{% endif %}`` to the :file:`preload.php.j2` template, required by
  Jinja engine to correctly generate the file. [drybjed_]

- Update the WikiMedia blacklist URL to use ``https://`` protocol. [drybjed_]


debops.dokuwiki v0.1.0 - 2015-03-26
-----------------------------------

Added
~~~~~

- Initial release [drybjed_]
