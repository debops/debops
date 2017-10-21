Changelog
=========

.. include:: includes/all.rst

**debops.salt**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is drybjed_.


`debops.salt master`_ - unreleased
----------------------------------

.. _debops.salt master: https://github.com/debops/ansible-salt/compare/v0.1.0...master


debops.salt v0.1.0 - 2017-05-02
-------------------------------

Added
~~~~~

- Add Changelog and update documentation. [drybjed_]

Changed
~~~~~~~

- Update upstream APT repository configuration. [thiagotalma_, drybjed_]

- Rename all variables from ``salt_*`` to ``salt__*`` to put them in a separate
  namespace. [drybjed_]

- Move role dependencies to the Ansible playbook. [drybjed_]

- Enable upstream APT repository on older OS releases. [drybjed_]

- Install backported version by default on Debian Jessie. [drybjed_]
