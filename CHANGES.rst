Changelog
=========

v0.1.0
------

*Unreleased*

- Initial release. [ypid]

- Wrote initial documentation. [ypid]

- Moved to `DebOps Contrib`_ (the role is still available under
  `ypid.snapshot_snapper`_ until it has been fully renamed to something like
  ``debops.cryptsetup``). [ypid]

- Changed namespace from ``snapshot_snapper_`` to ``snapshot_snapper__``.
  ``snapshot_snapper_[^_]`` variables are hereby deprecated and you might need
  to update your inventory. This oneliner might come in handy to do this.

  .. code:: shell

     git ls-files -z | find -type f -print0 | xargs --null sed --in-place --regexp-extended 's/(snapshot_snapper)_([^_])/\1__\2/g'

  [ypid]

- Use the `loop control feature <https://docs.ansible.com/ansible/playbooks_loops.html>`_
  of Ansible 2.1 and thus require Ansible 2.1. [ypid]

- Implemented automatic reinitialization of volume snapshots after a volume
  has been reformatted. [ypid]

.. _ypid.snapshot_snapper: https://galaxy.ansible.com/ypid/snapshot_snapper/
.. _DebOps Contrib: https://github.com/debops-contrib/
