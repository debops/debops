Changelog
=========

.. include:: includes/all.rst

**debops.apache**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops.apache v0.1.0 - unreleased
----------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Add/Set the default `Referrer Policy`_ to ``no-referrer`` and made it
  configurable via :ref:`item.http_referrer_policy <apache__ref_vhosts_http_referrer_policy>`.
  [ypid_]

Fixed
~~~~~

- Fixed usage of :envvar:`apache__dependent_packages` for ``debops.apache``.
  Previously the variable was only considered when handed to the ``debops.apache/env`` role.
  Note that all dependency variables should be passed to the main
  ``debops.apache`` role to avoid confusion. :envvar:`apache__dependent_packages` now
  only works when passed to the main role.
