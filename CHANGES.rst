Changelog
=========

**debops.unattended_upgrades**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.

`debops.unattended_upgrades master`_ - unreleased
-------------------------------------------------

.. _debops.unattended_upgrades master: https://github.com/debops/ansible-unattended_upgrades/compare/v0.1.4...master

Added
~~~~~

- ``state`` option for :envvar:`unattended_upgrades__blacklist` and similar
  lists when using the dictionary notation. This replaces the removed
  ``when`` option. The ``state`` allows to remove entries from the blacklist
  which ``when`` did not. [ypid]

- Support dictionary notation for :envvar:`unattended_upgrades__origins` and
  :envvar:`unattended_upgrades__dependent_origins` lists. [ypid]

- Documentation for :envvar:`unattended_upgrades__origins`.

Changed
~~~~~~~

- Reworked role to meet the latest DebOps standards. [ypid]

Fixed
~~~~~

- Fixed example for :envvar:`unattended_upgrades__blacklist` which is expected
  to be a regular expression and a mix between glob and regular expression.
  The previous given example also works for some reason so this fix is merely
  to follow the upstream documentation more strictly.
  [ypid]

Removed
~~~~~~~

- ``when`` option from :envvar:`unattended_upgrades__blacklist` and similar
  lists when using the dictionary notation. It has been superseded by the
  ``state`` option to allow to remove entries from the blacklist. [ypid]

`debops.unattended_upgrades v0.1.4`_ - 2016-03-02
-------------------------------------------------

.. _debops.unattended_upgrades v0.1.4: https://github.com/debops/ansible-unattended_upgrades/compare/v0.1.3...v0.1.4

Fixed
~~~~~

- Fix issue with role import on Ansible Galaxy. [drybjed]

`debops.unattended_upgrades v0.1.3`_ - 2016-03-02
-------------------------------------------------

.. _debops.unattended_upgrades v0.1.3: https://github.com/debops/ansible-unattended_upgrades/compare/v0.1.2...v0.1.3

Added
~~~~~

- Add support for conditional package blacklisting. [drybjed]

`debops.unattended_upgrades v0.1.2`_ - 2016-02-22
-------------------------------------------------

.. _debops.unattended_upgrades v0.1.2: https://github.com/debops/ansible-unattended_upgrades/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Use more granular lookup for security and release origins.

  Due to the ``unattended-upgrades`` `Debian Bug #704087 <https://bugs.debian.org/704087>`_
  on Debian Wheezy which stops the upgrades from being performed,
  ``debops.unattended_upgrades`` role will now use more granular lookup strings
  to select security and release origin patterns for current OS release.
  [drybjed]

`debops.unattended_upgrades v0.1.1`_ - 2016-02-10
-------------------------------------------------

.. _debops.unattended_upgrades v0.1.1: https://github.com/debops/ansible-unattended_upgrades/compare/v0.1.0...v0.1.1

Removed
~~~~~~~

- Rename all variables to create a virtual namespace. [drybjed]

debops.unattended_upgrades v0.1.0 - 2016-02-09
----------------------------------------------

Added
~~~~~

- Initial release. [drybjed]

