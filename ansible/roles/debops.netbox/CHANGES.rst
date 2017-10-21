.. _netbox__ref_changelog:

Changelog
=========

.. include:: includes/all.rst

**debops.netbox**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed.


`debops.netbox master`_ - unreleased
------------------------------------

.. _debops.netbox master: https://github.com/debops/ansible-netbox/compare/v0.1.1...master


`debops.netbox v0.1.1`_ - 2017-02-14
------------------------------------

.. _debops.netbox v0.1.1: https://github.com/debops/ansible-netbox/compare/v0.1.0...v0.1.1

Fixed
~~~~~

- Make sure that the ``pip`` and ``setuptools`` modules are upgraded in the
  NetBox ``virtualenv`` environment to avoid an issue with missing
  ``packaging.version`` Python module. [drybjed_]


debops.netbox v0.1.0 - 2016-10-20
---------------------------------

Added
~~~~~

- Initial release. [drybjed_]
