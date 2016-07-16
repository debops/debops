Changelog
=========

**debops.dokuwiki**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.


`debops.dokuwiki master`_ - unreleased
--------------------------------------

.. _debops.dokuwiki master: https://github.com/debops/ansible-environment/compare/v0.2.1...master

Added
~~~~~

- Add ``tag`` plugin with required ``pagelist`` plugin for page tagging
  support. [drybjed]

Changed
~~~~~~~

- Remove hard role dependencies. Configuration of other roles is moved to
  ``defaults/main.yml`` and updated playbook is added in the
  ``debops.dokuwiki`` documentation. Role now uses ``debops.php`` role instead
  of ``debops.php5`` to configure PHP support. [drybjed]

- Update documentation and Changelog. [drybjed]

- Remove ``no_log: True`` from tasks that clone different ``git`` repositories.
  [drybjed]

Fixed
~~~~~

- Fix Ansible 2.1 deprecation warnings. [drybjed]


`debops.dokuwiki v0.2.0`_ - 2015-09-03
--------------------------------------

.. _debops.dokuwiki v0.2.0: https://github.com/debops/ansible-environment/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add ``gallery`` DokuWiki plugin to list of default plugins. [drybjed]

Changed
~~~~~~~

- Use a static, configurable filename for ``nginx`` configuration. This helps
  when wiki domain is changed on an existing installation.

  This change will generate a new nginx configuration file. Depending on your
  server layout you might need to remove at least the symlink to the old
  DokuWiki configuration file to prevent ``nginx`` server from failing to
  restart properly. [drybjed]

- Change the ``dokuwiki`` system user home directory to be the same as website
  directory, based on ``ansible_local.nginx.www`` local Ansible fact. [drybjed]

- Add missing ``{% endif %}`` to the ``preload.php.j2`` template, required by
  Jinja engine to correctly generate the file. [drybjed]

- Update the WikiMedia blacklist URL to use ``https://`` protocol. [drybjed]


debops.dokuwiki v0.1.0 - 2015-03-26
-----------------------------------

Added
~~~~~

- Initial release [drybjed]
