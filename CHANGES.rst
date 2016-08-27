Changelog
=========

.. include:: includes/all.rst

**debops.hashicorp**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.hashicorp master`_ - unreleased
---------------------------------------

.. _debops.hashicorp master: https://github.com/debops/ansible-hashicorp/compare/v0.1.1...master


`debops.hashicorp v0.1.1`_ - 2016-08-27
---------------------------------------

.. _debops.hashicorp v0.1.1: https://github.com/debops/ansible-hashicorp/compare/v0.1.0...v0.1.1

Added
-----

- Enable ``vault-ssh-helper`` on the list of known HashiCorp applications,
  v0.1.2 release is compatible with the installation method. [drybjed]

Changed
~~~~~~~

- Utilize the full power of the DebOps_ documentation format using RST
  hyperlinks and Sphinx inline syntax. [ypid_]

- Update default application versions of ``terraform`` (v0.7.2) and ``nomad``
  (v0.4.1). [drybjed]


debops.hashicorp v0.1.0 - 2016-07-22
------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
