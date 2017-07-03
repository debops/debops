.. _apt__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.apt**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.

Refer to the :ref:`apt__ref_upgrade_notes` when you intend to upgrade to a
new release.


`debops.apt master`_ - unreleased
---------------------------------

.. _debops.apt master: https://github.com/debops/ansible-apt/compare/v0.5.0...master


`debops.apt v0.5.0`_ - 2017-07-03
---------------------------------

.. _debops.apt v0.5.0: https://github.com/debops/ansible-apt/compare/v0.4.4...v0.5.0

Added
~~~~~

- Add the Ansible local fact ``default_sources_map`` which contains a
  dictionary with distribution name as key containing a list of default sources
  for each distribution. ``default_mirrors`` is equivalent to
  ``default_sources_map[apt__distribution]``.  [ypid_]

- Add support for the ARM based BeagleBoard family. Tested with a BeagleBone
  Black. [ypid_]

- Add support for the `Devuan Jessie <https://devuan.org/>`_ Linux
  distribution. [evilham]

Changed
~~~~~~~

- Filter the Ansible local facts ``default_mirrors`` to only provide the
  default APT mirrors that are relevant to the current OS distribution. This
  way the list can be used by other Ansible roles for APT mirror information.
  [drybjed_, ypid_]

- Use debops__tpl_macros.js_ to cleanup redundant code. [ypid_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

- Update the default variables for Debian Stretch as the new stable release so
  that backports get enabled for Stretch by default. [ypid_]

Fixed
~~~~~

- Fix handling of ``option`` and ``options`` from :envvar:`apt__sources` and add
  missing documentation. [ypid_]

- Properly handle singular and plural options for :envvar:`apt__sources`.
  Previously certain edge cases might have caused an issue.
  This has been achieved by cleaning up the templates to map all inputs to the
  plural variant and eliminating redundant code.
  Redundancy is the natural enemy of all Ansible role maintainers and should be
  avoided. [ypid_]


`debops.apt v0.4.4`_ - 2017-03-24
---------------------------------

.. _debops.apt v0.4.4: https://github.com/debops/ansible-apt/compare/v0.4.3...v0.4.4

Changed
~~~~~~~

- Switch the official Debian repository source to ``http://deb.debian.org/debian``
  due to `the deprecation of the httpredir service <https://lists.debian.org/debian-mirrors/2017/02/msg00000.html>`_.
  [drybjed_]


`debops.apt v0.4.3`_ - 2016-11-23
---------------------------------

.. _debops.apt v0.4.3: https://github.com/debops/ansible-apt/compare/v0.4.2...v0.4.3

Added
~~~~~

- Improve autodetection of APT sources on Raspbian and Ubuntu, as well as
  Debian Testing/Unstable releases. [grantma_]


`debops.apt v0.4.2`_ - 2016-11-22
---------------------------------

.. _debops.apt v0.4.2: https://github.com/debops/ansible-apt/compare/v0.4.1...v0.4.2

Added
~~~~~

- Add support for filtering APT distribution sources and repositories according
  to the system architecture. Only one architecture can be specified at a time
  for a given source entry. [drybjed_]

- Add :envvar:`apt__distribution_release_map` YAML dictionary which keeps the
  information about released OS distributions which have official security
  repositories. [drybjed_]

Changed
~~~~~~~

- Update the :file:`/etc/apt/sources.list` template so that it tracks
  repository suites for each URI. This should allow configuration of separate
  source entries from the same repository but with different suites. [drybjed_]

- The Debian Security repository will be enabled only on official releases, on
  hosts with Debian Unstable (Sid) it will be automatically disabled.
  [drybjed_]

- Ubuntu Security repository will be enabled only on supported architectures
  (``amd64``, ``i386``). On other architectures, Ubuntu Ports Security
  repository will be enabled instead. [drybjed_]


`debops.apt v0.4.1`_ - 2016-11-03
---------------------------------

.. _debops.apt v0.4.1: https://github.com/debops/ansible-apt/compare/v0.4.0...v0.4.1

Added
~~~~~

- Add an entry for an alternative Debian Security repository that's present in
  the :file:`/etc/apt/sources.list` on Debian Stretch. This entry is disabled
  by default to not include duplicates in the generated sources configuration,
  but still needs to be present for ``debops.apt`` to recognize it correctly.
  [drybjed_]


`debops.apt v0.4.0`_ - 2016-10-04
---------------------------------

.. _debops.apt v0.4.0: https://github.com/debops/ansible-apt/compare/v0.3.0...v0.4.0

Added
~~~~~

- The role now knows about free vs non-free APT distribution repositories. The
  non-free repositories are enabled on hardware-based hosts to prepare for the
  unfortunate case where non-free firmware packages are required; otherwise only
  repositories containing Free Software (``main`` and, on Ubuntu, ``universe``)
  are enabled. This can be controlled by the :envvar:`apt__nonfree` variable.

  The role exposes an additional Ansible fact that detects the availability of
  the ``non-free`` distribution sources and can be used by other Ansible roles
  to check if non-free packages can be installed. [drybjed_]

- The ``distribution`` and ``distribution_release`` parameters allow you to
  conditionally enable APT keys/repositories.
  This allows for example to enable certain repository only when ``Debian`` is
  found as the host's OS. [drybjed_]

- Management of :file:`/etc/apt/sources.list` file is controlled by a separate
  variable, :envvar:`apt__sources_deploy_state`. [drybjed_]

- Lists of APT keys, APT repositories and distribution sources are now properly
  documented. [drybjed_]

- The OS distribution and release detection now uses Ansible facts managed by
  the debops.core_ role. With these enabled, ``debops.apt`` should
  correctly detect a Debian Testing installation and configure it
  accordingly. [drybjed_]

- The role looks for original APT repositories configured on a host in the
  diverted :file:`/etc/apt/sources.list` file and includes them in the generated
  configuration file with higher precedence than the default mirrors, with
  the assumption that the original mirrors are closer than the role defaults.
  This can be controlled by the default variables. [drybjed_]

Changed
~~~~~~~

- The ``apt__update_cache_early`` variable has been renamed to
  :envvar:`apt__cache_valid_time`. [drybjed_]

- The ``apt__sources_types`` variable has been renamed to
  :envvar:`apt__source_types`. [drybjed_]

- The OS distribution and release detection has been redesigned and should
  allow for more flexibility in regards to different operating systems. [drybjed_]

- Some of the APT repository/source list parameters have been renamed. Check
  the documentation for currently used parameters. [drybjed_]

- The Ansible local fact file has been changed into a Python script and is now
  more dynamic, and provides additional information about original APT sources,
  used internally. [drybjed_]

- The task list has been streamlined and merged into one file. The Ansible
  facts are configured at the beginning to allow for the role to gather
  information about original APT sources. [drybjed_]

- Expose configuration of installation or removal of recommended or suggested
  packages in default variables. [drybjed_]

Removed
~~~~~~~

- The variables set in ``vars/*.yml`` variables as well as the file lookup
  mechanism have been removed. Their configuration lives on in the improved
  ``apt__*_sources`` lists. [drybjed_]

- The ``apt__*_mirrors`` variables have been removed, the functionality is now
  merged with ``apt__*_sources`` variables. [drybjed_]

- The ``apt__*_delayed`` variables have been removed. You can use the ``state``
  parameter with Ansible local facts to get an equivalent functionality. See
  the documentation for more details. [drybjed_]

- Remove the ``aptitude`` configuration using a static template file. Existing
  configuration files are not changed. [drybjed_].


`debops.apt v0.3.0`_ - 2016-09-14
---------------------------------

.. _debops.apt v0.3.0: https://github.com/debops/ansible-apt/compare/v0.2.1...v0.3.0

Removed
~~~~~~~

- Remove support for :command:`apt-listchanges` (moved to a separate role) and
  ``apticron`` packages. [drybjed_]

- Remove support for APT proxy configuration, it is moved to a separate Ansible
  role. [drybjed_]


`debops.apt v0.2.1`_ - 2016-09-09
---------------------------------

.. _debops.apt v0.2.1: https://github.com/debops/ansible-apt/compare/v0.2.0...v0.2.1

Added
~~~~~

- Added support for both http and https repositories in case of internet proxy.
  Moved ``apt__proxy_url`` to ``apt__http_proxy_url`` and added
  ``apt__https_proxy_url``. [tallandtree_]

Changed
~~~~~~~

- Update documentation and Changelog. [ypid_, drybjed_]


`debops.apt v0.2.0`_ - 2016-07-14
---------------------------------

.. _debops.apt v0.2.0: https://github.com/debops/ansible-apt/compare/v0.1.0...v0.2.0

Added
~~~~~

- Added ``apt__proxy_bypass_for_bugs_debian_org`` which you can enable if you
  hit a problem with a proxy server not allowing access to
  https://bugs.debian.org. [ypid_]

Changed
~~~~~~~

- Updated/Reworked documentation. [ypid_]

- Changed namespace from ``apt_`` to ``apt__``.
  ``apt_[^_]`` variables are hereby deprecated and you might need to
  update your inventory. This oneliner might come in handy to do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(apt)_([^_])/\1__\2/g;s/apt__(key|repository|preferences|cacher)/apt_\1/g;s/apt_keys_delayed/apt__keys_delayed/g;'

  [ypid_]

- Use backported :program:`irqbalance` on Debian Jessie. [ypid_]

- Rename forgotten ``apt_keys`` variable. [drybjed_]

Removed
~~~~~~~

- Remove support for :program:`apt-cacher-ng`. The new role debops.apt_cacher_ng_
  handles this now. The overloaded :command:`apt` variable as been split into
  :envvar:`apt__enabled` and apt__proxy. [ypid_]

- Removed debops.apt_preferences_ as hard role dependency and added
  :envvar:`apt__apt_preferences__dependent_list` which you can feed to
  debops.apt_preferences_ in your playbook. [ypid_]

- Delete previously created ``apt_preferences`` entries. They have been moved
  to the debops.apt_install_ role instead. [drybjed_]

- Clean up package lists and remove unused tasks. The functionality has been
  moved to the debops.apt_install_ role. [drybjed_]


debops.apt v0.1.0 - 2016-05-26
------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Support "stacked inventory variables" for APT sources, repositories, keys and
  lists of mirrors. [drybjed_]

- Added :envvar:`apt__remove_default_configuration` option which defaults to true.
  This ensures that :file:`/etc/apt/apt.conf` is absent. [ypid_]

- Use backported :program:`apt-cacher-ng` on Debian Jessie. [ypid_]

- Allow to modify APT sections without defining :envvar:`apt__default_sources` by
  using the added ``apt__sources_sections`` variable. [ypid_]

Changed
~~~~~~~

- Switch the default Debian mirror to new official redirector at
  http://httpredir.debian.org/. [drybjed_]

- Remove support for ``unattended-upgrades``. The new role
  debops.unattended_upgrades_ handles this now. The ``debops.apt`` role will
  have a task for some time which removes old configuration files related to
  ``unattended-upgrades`` to clean up the old systems. [drybjed_]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed_]
