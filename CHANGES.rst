.. _rstudio_server__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.rstudio_server**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.rstudio_server master`_ - unreleased
--------------------------------------------

.. _debops.rstudio_server master: https://github.com/debops/ansible-rstudio_server/compare/v0.1.0...master

Added
~~~~~

- Using a set of variables you can specify a list of UNIX accounts which should
  be allowed to use RStudio Server; any existing accounts will be automatically
  added to the authentication group. [drybjed_]

Changed
~~~~~~~

- The role now checks if the required ``libssl1.0.0`` and ``rstudio-server``
  ``.deb`` packages are available through APT, and if not, it can download them
  directly and install via :command:`dpkg`. [drybjed_]

- Support for Debian Wheezy has been removed, role works with Debian Jessie and
  Debian Stretch. See :ref:`rstudio_server__ref_installation_issues` for more
  details. [drybjed_]

- All role variables have been renamed from ``rstudio_server_*`` to
  ``rstudio_server__*`` to put them in a separate namespace. You will need to
  update your inventory. [drybjed_]

- RStudio Server configuration has been moved from templates and into default
  variables, so it can be easier to change if needed. [drybjed_]

- Role dependencies have been moved from the :file:`meta/main.yml` file to the
  playbook level. [drybjed_]

- The default :command:`nginx` configuration should now support WebSocket
  connections. [drybjed_]

Removed
~~~~~~~

- The management of the R environment has been removed from the role and is now
  done by a separate Ansible role, ``debops.cran``. [drybjed_]


debops.rstudio_server v0.1.0 - 2015-05-15
-----------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
