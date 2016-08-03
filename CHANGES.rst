Changelog
=========

v0.2.0
------

*Unreleased*

- Add Changelog. [ypid]

- Added support to only configure :file:`/etc/samba/smb.conf` without
  installing the Samba daemon. [ypid]

- Converted :file:`defaults/main.yml` to new documentation format and improved
  documentation. [ypid]

- Put kernel modules loaded by this role to a separate file under
  :file:`/etc/modules-load.d` managed by this role. [ypid]

- Changed variable namespace from ``samba_`` to ``samba__``.
  ``samba_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(samba)_([^_])/\1__\2/g;'

  [ypid]

- Allow to change "name resolve order" in the global section using
  :envvar:`samba__name_resolve_order`. [ypid]

v0.1.0
------

*Unreleased*

- First release. [drybjed]
