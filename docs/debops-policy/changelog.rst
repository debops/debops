Changelog
=========

.. include:: ../includes/global.rst

**debops-policy**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current repository maintainer is drybjed_.


`debops-policy master`_ - unreleased
------------------------------------

.. _debops-policy master: https://github.com/debops/debops-policy/compare/v0.1.0...master

Added
~~~~~

- Add first draft of Code Standards Policy. [drybjed_]

Changed
~~~~~~~

- Major rework and enhancement of Code Standards Policy. [ganto_]


debops-policy v0.1.0 - 2016-09-04
---------------------------------

Added
~~~~~

- Updated the repository layout to be compatible with the rest of the DebOps
  documentation. [drybjed_]

- Added a draft of the :ref:`debops_policy__organizational_structure` and
  explanation of :ref:`debops_policy__distributed_development_model`, as well a
  draft of the :ref:`debops_policy__code_signing_policy` used by the project.
  [drybjed_, ypid_]

- Wrote initial :ref:`debops_policy__security_policy`. [ypid_]

- Added "Project Admin" role to :ref:`debops_policy__organizational_structure`. [ypid_]

- Added first draft of the software source policy. [drybjed_]

Changed
~~~~~~~

- Use `RFC2119`_ and `ISO 8601`_ for the :ref:`debops_policy__security_policy`. [ypid_]

- Renamed "Role Authors" and "Role Maintainers" to "Authors" and "Maintainers"
  to keep the roles in the :ref:`debops_policy__organizational_structure` more generic. [ypid_]

- Clarified that DebOps Developer don’t automatically have more write
  privileges. [ypid_]

- Reviewed and compared with other policies and adapted where useful. [AnBuKu_, ypid_]

- Review and minor improvements for the software source policy. [ypid_]
