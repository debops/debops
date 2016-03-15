Changelog
=========


v0.1.0
------

*Unreleased*

- Initial release. [ypid]

- Renamed ``apparmor_enable`` to ``apparmor__enabled``. [ypid]

- Changed namespace from ``apparmor_`` to ``apparmor__``.
  ``apparmor_[^_]`` variables are hereby deprecated and you might need to
  update your inventory. This oneliner might come in handy to do this.

  .. code:: shell

     git ls-files -z | find -type f -print0 | xargs --null sed --in-place --regexp-extended 's/(apparmor)_([^_])/\1__\2/g'

  [ypid]
