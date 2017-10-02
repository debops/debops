Changelog
=========

.. include:: includes/all.rst

**debops.apt_proxy**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.apt_proxy master`_ - unreleased
---------------------------------------

.. _debops.apt_proxy master: https://github.com/debops/ansible-apt_proxy/compare/v0.1.0...master

Added
~~~~~

- Add proxy online detection support to silently skip/ignore temporally offline proxies.
  The main use case for this feature are workstations and home servers which
  might not always be able to reach the proxy server but should still be able
  to update/install packages.
  It is therefore disabled by default which is probably the best setting for
  production data center environments. [ypid_]


debops.apt_proxy v0.1.0 - 2016-09-14
------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
