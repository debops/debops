Changelog
=========

.. include:: includes/all.rst

**debops-contrib.x2go_server**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.

debops-contrib.x2go_server v0.1.0 - unreleased
----------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

Changed
~~~~~~~

- Rename ``x2go_server__apt_repo_key_fingerprint_override_map`` to :envvar:`x2go_server__apt_repo_key_fingerprint_map`

  Rename ``x2go_server__upstream_repository_override_map`` to :envvar:`x2go_server__upstream_repository_map`.

  And just use a default entry. [ypid_]

- Require Ansible v2.1.3 to mitigate CVE-2016-8614:

  ::

    apt_key module not properly validating keys in some situations - resolved in Ansible 2.1.3/2.2.

  Refer to `Ansible Security`_ and `apt_key module does not verify key fingerprints <https://github.com/ansible/ansible-modules-core/issues/5237>`_
  for details.

  Note that Ansible currently does not check min version of roles (`Tracked upstream <https://github.com/ansible/ansible/issues/18375>`_).
  Please only use v2.1.3 or above to run this role! [ypid_]
