Changelog
=========

.. include:: includes/all.rst

**debops-contrib.snapshot_snapper**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/0.3.0/>`__.

The current role maintainer_ is ypid_.


debops-contrib.snapshot_snapper v0.1.0 - unreleased
---------------------------------------------------

Added
~~~~~

- Initial coding and design. [ypid_]

- Wrote initial documentation. [ypid_]

- Implemented automatic reinitialization of volume snapshots after a volume
  has been reformatted. [ypid_]

Changed
~~~~~~~

- Moved to `DebOps Contrib`_ (the role is still available under
  ``ypid.snapshot_snapper`` until it has been fully renamed). [ypid_]

- Changed namespace from ``snapshot_snapper_`` to ``snapshot_snapper__``.
  ``snapshot_snapper_[^_]`` variables are hereby deprecated and you might need
  to update your inventory. This oneliner might come in handy to do this.

  .. code-block:: shell

     git ls-files -z | find -type f -print0 | xargs --null sed --in-place --regexp-extended 's/(snapshot_snapper)_([^_])/\1__\2/g'

  [ypid_]

- Use the `loop control feature <https://docs.ansible.com/ansible/playbooks_loops.html>`_
  of Ansible 2.1 and thus require Ansible 2.1. [ypid_]

- Include the ``mlocate`` package in the default package list as the role
  requires it currently. More rework is needed. [ypid_]

Fixed
~~~~~

- Fixed recognition of empty ``SNAPPER_CONFIGS`` set in
  :file:`/etc/default/snapper` and don’t write a second ``SNAPPER_CONFIGS``
  variable in this case.
  Previous to this fix, snapshots where not automatically created because a
  second ``SNAPPER_CONFIGS`` (empty) set was added to the file.
  [ypid_]
