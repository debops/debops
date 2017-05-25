Changelog
=========

.. include:: includes/all.rst

**debops.hashicorp**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.hashicorp master`_ - unreleased
---------------------------------------

.. _debops.hashicorp master: https://github.com/debops/ansible-hashicorp/compare/v0.1.2...master


`debops.hashicorp v0.1.2`_ - 2017-05-25
---------------------------------------

.. _debops.hashicorp v0.1.2: https://github.com/debops/ansible-hashicorp/compare/v0.1.1...v0.1.2

Changed
~~~~~~~

- Update documentation and Changelog. [ypid_, drybjed_]

- Use the ``become`` method explicitly in Ansible block to ensure that
  ``become_user`` works. [ypid_]

- Use the ``apt_key`` Ansible module to import Hashicorp GPG key instead of
  ``shell`` command. [ypid_]

- Use more specific regexp matching during signature verification. [ypid_]

- Use the ``remote_src`` parameter instead of ``copy`` in the ``unarchive``
  task due to the latter being deprecated. [ypid_]

- Update the version of :command:`consul`, :command:`consul-replicate`,
  :command:`consul-template`, :command:`envconsul`, :command:`nomad`,
  :command:`packer`, :command:`serf`, :command:`terraform`, :command:`vault`
  and :command:`vault-ssh-helper` to their latest releases. [drybjed_]


`debops.hashicorp v0.1.1`_ - 2016-08-27
---------------------------------------

.. _debops.hashicorp v0.1.1: https://github.com/debops/ansible-hashicorp/compare/v0.1.0...v0.1.1

Added
-----

- Enable ``vault-ssh-helper`` on the list of known HashiCorp applications,
  v0.1.2 release is compatible with the installation method. [drybjed_]

Changed
~~~~~~~

- Utilize the full power of the DebOps_ documentation format using RST
  hyperlinks and Sphinx inline syntax. [ypid_]

- Update default application versions of ``terraform`` (v0.7.2) and ``nomad``
  (v0.4.1). [drybjed_]


debops.hashicorp v0.1.0 - 2016-07-22
------------------------------------

Added
~~~~~

- Initial release. [drybjed_]
