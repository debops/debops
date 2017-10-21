Changelog
=========

*Unreleased*

Fixed
~~~~~

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

v0.2.0
------

*Released: 2016-05-19*

- Fix deprecation warnings in Ansible 2.1.0. [ypid]

- Updated example playbook and inventory in the documentation. [ypid]

- Fixed Ansible check mode support. [ypid]

- Moved lookup files to templates directory to allow them to be found. [ypid]

- Removed ``virt_net`` and ``virt_pool`` from the role and require Ansible 2.0
  which includes them. [ypid]

- Changed variable namespace from ``libvirt_`` to ``libvirt__``.
  ``libvirt_[^_]`` variables are hereby deprecated.

  You might need to update your inventory. This oneliner might come in handy to
  do this:

  .. code:: shell

     git ls-files -z | xargs --null -I '{}' find '{}' -type f -print0 | xargs --null sed --in-place --regexp-extended 's/\<(libvirt)_([^_])/\1__\2/g;'

  [ypid]

v0.1.1
------

*Released: 2015-07-27*

- Fix documentation formatting. [drybjed]

v0.1.0
------

*Released: 2015-07-27*

- Initial release. [drybjed]
