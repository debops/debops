Changelog
=========

.. include:: includes/all.rst

**debops.apt_preferences**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.apt_preferences master`_ - unreleased
---------------------------------------------

.. _debops.apt_preferences master: https://github.com/debops/ansible-apt_preferences/compare/v0.2.4...master

Fixed
~~~~~

- :envvar:`apt_preferences__debian_stable_default_preset_list` did not handle
  the case where the ``ansible_distribution_release`` is not the current Debian
  stable release. Consider you are running Debian stable and have included
  Debian testing repositories. Now a new Debian version is released and testing
  becomes the new stable. Because the preset pinned the currently running
  release by codename and everything else by suite the pin for "testing" does
  not match anymore and the new stable gets the default priority meaning
  it has the same as packages from the currently running release.
  This has been fixed by pinning packages from the stable suite to 100 if they
  did not come from the currently running release. [ypid_]


`debops.apt_preferences v0.2.4`_ - 2017-05-02
---------------------------------------------

.. _debops.apt_preferences v0.2.4: https://github.com/debops/ansible-apt_preferences/compare/v0.2.3...v0.2.4

Added
~~~~~

- Support multiline ``item.reason``. Refer to :ref:`apt_preferences__list` for more details and examples. [ypid_]


`debops.apt_preferences v0.2.3`_ - 2016-09-04
---------------------------------------------

.. _debops.apt_preferences v0.2.3: https://github.com/debops/ansible-apt_preferences/compare/v0.2.2...v0.2.3

Changed
~~~~~~~

- Fix the ``replace`` filter nesting in the automatically generated filenames
  so that the correct variables are replaced. [drybjed_]


`debops.apt_preferences v0.2.2`_ - 2016-09-04
---------------------------------------------

.. _debops.apt_preferences v0.2.2: https://github.com/debops/ansible-apt_preferences/compare/v0.2.1...v0.2.2

Changed
~~~~~~~

- Sanitize file name generated from ``item.by_role`` by replacing dots with
  underscores. [ypid_]

- Update documentation. [drybjed_]


`debops.apt_preferences v0.2.1`_ - 2016-06-28
---------------------------------------------

.. _debops.apt_preferences v0.2.1: https://github.com/debops/ansible-apt_preferences/compare/v0.2.0...v0.2.1

Added
~~~~~

- Support singular and plural versions of the ``item.package`` parameter, as
  well as both string an YAML list variants. [drybjed_]

- Add support for ``item.state`` parameter and deprecate the alternatives.
  [drybjed_]

Changed
~~~~~~~

- Update list of Ubuntu releases. [drybjed_]


`debops.apt_preferences v0.2.0`_ - 2016-06-14
---------------------------------------------

.. _debops.apt_preferences v0.2.0: https://github.com/debops/ansible-apt_preferences/compare/v0.1.3...v0.2.0

Added
~~~~~

- Added :envvar:`apt_preferences__preset_list` for advanced users. [ypid_]

Changed
~~~~~~~

- Changed variable namespace from ``apt_preferences_`` to ``apt_preferences__``.
  ``apt_preferences_[^_]`` variables are hereby deprecated but are currently
  still supported to allow a soft migration.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(apt_preferences)_([^_])/\1__\2/g;'

  [ypid_]

- Use marker levels in vim markers to eliminate empty spaces. [drybjed_]


`debops.apt_preferences v0.1.3`_ - 2016-02-07
---------------------------------------------

.. _debops.apt_preferences v0.1.3: https://github.com/debops/ansible-apt_preferences/compare/v0.1.2...v0.1.3

Changed
~~~~~~~

- Fix deprecation warnings in Ansible 2.1.0. [drybjed_]


`debops.apt_preferences v0.1.2`_ - 2015-11-13
---------------------------------------------

.. _debops.apt_preferences v0.1.2: https://github.com/debops/ansible-apt_preferences/compare/v0.1.1...v0.1.2

Added
~~~~~

- Add support for ``item.when`` parameter, which introduces a way to
  enable/disable a particular pin conditionally. [drybjed_]

Changed
~~~~~~~

- Support ``item.role`` as an alternative parameter. [drybjed_]

- Check ``item.delete`` explicitly as a boolean. [drybjed_]


`debops.apt_preferences v0.1.1`_ - 2015-10-15
---------------------------------------------

.. _debops.apt_preferences v0.1.1: https://github.com/debops/ansible-apt_preferences/compare/v0.1.0...v0.1.1

Changed
~~~~~~~

- Fixed documentation spelling. [ypid_]

debops.apt_preferences v0.1.0 - 2015-10-15
------------------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Clean up documentation. [drybjed_]
