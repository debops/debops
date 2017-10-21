Changelog
=========

.. include:: includes/all.rst

**debops.samba**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/>`_.

The current role maintainer_ is drybjed_.


debops.samba v0.1.0 - unreleased
--------------------------------

Added
~~~~~

- First release. [drybjed_]

- Changelog. [ypid_]

- Support to configure :file:`/etc/samba/smb.conf` without
  installing the Samba daemon. [ypid_]

- Put kernel modules loaded by this role to a separate file under
  :file:`/etc/modules-load.d` managed by this role. [ypid_]

- Allow to change "name resolve order" in the global section using
  :envvar:`samba__name_resolve_order`. [ypid_]

Changed
~~~~~~~

- Converted :file:`defaults/main.yml` to new documentation format and improved
  documentation. [ypid_]

- Changed variable namespace from ``samba_`` to ``samba__``.
  ``samba_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(samba)_([^_])/\1__\2/g;'

  [ypid_]

- Removed SO_RCVBUF and SO_SNDBUF legacy socket options. [bfabio_]
