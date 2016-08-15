.. _apt__ref_changelog:

Changelog
=========

**debops.apt**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`_
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer is drybjed.

`debops.apt master`_ - unreleased
---------------------------------

.. _debops.apt master: https://github.com/debops/ansible-apt/compare/v0.2.0...master

Added
~~~~~

- Added support for both http and https repositories in case of internet proxy.
  Moved apt__proxy_url to :any:`apt__http_proxy_url` and 
  :any:`added apt__https_proxy_url`.

`debops.apt v0.2.0`_ - 2016-07-14
---------------------------------

.. _debops.apt v0.2.0: https://github.com/debops/ansible-apt/compare/v0.1.0...v0.2.0

- Remove support for :program:`apt-cacher-ng`. The new role ``debops.apt_cacher_ng``
  handles this now. The overloaded :command:`apt` variable as been split into
  :any:`apt__enabled` and apt__proxy. [ypid]

- Added :any:`apt__proxy_bypass_for_bugs_debian_org` which you can enable if you
  hit a problem with a proxy server not allowing access to
  https://bugs.debian.org. [ypid]

- Removed ``debops.apt_preferences`` as hard role dependency and added
  :any:`apt__apt_preferences__dependent_list` which you can feed to
  ``debops.apt_preferences`` in your playbook. [ypid]

- Updated/Reworked documentation. [ypid]

- Changed namespace from ``apt_`` to ``apt__``.
  ``apt_[^_]`` variables are hereby deprecated and you might need to
  update your inventory. This oneliner might come in handy to do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(apt)_([^_])/\1__\2/g;s/apt__(key|repository|preferences|cacher)/apt_\1/g;s/apt_keys_delayed/apt__keys_delayed/g;'

  [ypid]

- Use backported :program:`irqbalance` on Debian Jessie. [ypid]

- Rename forgotten ``apt_keys`` variable. [drybjed]

- Delete previously created ``apt_preferences`` entries. They have been moved
  to the ``debops.apt_install`` role instead. [drybjed]

- Clean up package lists and remove unused tasks. The functionality has been
  moved to the ``debops.apt_install`` role. [drybjed]

`debops.apt v0.1.0`_ - 2016-05-26
---------------------------------

.. _debops.apt v0.1.0: https://github.com/debops/ansible-apt/compare/v0.1.0...v0.2.0

Added
~~~~~

- Add Changelog. [drybjed]

- Support "stacked inventory variables" for APT sources, repositories, keys and
  lists of mirrors. [drybjed]

- Added :any:`apt__remove_default_configuration` option which defaults to true.
  This ensures that :file:`/etc/apt/apt.conf` is absent. [ypid]

- Use backported :program:`apt-cacher-ng` on Debian Jessie. [ypid]

- Allow to modify APT sections without defining ``apt__default_sources`` by
  using the added ``apt__sources_sections`` variable. [ypid]

Changed
~~~~~~~

- Switch the default Debian mirror to new official redirector at
  http://httpredir.debian.org/. [drybjed]

- Remove support for ``unattended-upgrades``. The new role
  ``debops.unattended_upgrades`` handles this now. The ``debops.apt`` role will
  have a task for some time which removes old configuration files related to
  ``unattended-upgrades`` to clean up the old systems. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]
