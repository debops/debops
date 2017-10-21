Changelog
=========

.. include:: includes/all.rst

**debops.nullmailer**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.nullmailer master`_ - unreleased
----------------------------------------

.. _debops.nullmailer master: https://github.com/debops/ansible-nullmailer/compare/v0.1.0...master

Fixed
~~~~~

- Fix ``item.starttls`` for :envvar:`nullmailer__remotes` which was ignored
  previously when set to ``False``. [ypid_]

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]


debops.nullmailer v0.1.0 - 2016-07-26
-------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
