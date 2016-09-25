.. _apt_install__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.apt_install**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_


`debops.apt_install master`_ - unreleased
-----------------------------------------

.. _debops.apt_install master: https://github.com/debops/ansible-apt_install/compare/v0.1.1...master

Added
~~~~~

- Install ``haveged`` by default on virtual machines excluding containers like
  LXC as suggested in https://bettercrypto.org/. [ypid_]


v0.1.1
------

*Released: 2016-05-28*

- Rewrote the 316 line :file:`templates/lookup/apt_install__all_packages.j2`
  template from scratch to make it maintainable and extensible in 42 lines of
  straight Jinja2 ;-). [ypid_]

- Implemented :envvar:`apt_install__conditional_whitelist_packages` previously
  known as ``apt__conditional_whitelist`` in debops.apt_. [ypid_]

- Updated and fixed up metadata and copyright. [ypid_]

- Small fixes in the documentation. [drybjed_]

v0.1.0
------

*Released: 2016-05-26*

- Initial release. [drybjed_]
