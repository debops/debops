Changelog
=========

v0.1.1
------

*Released: 2016-05-28*

- Rewrote the 316 line :file:`templates/lookup/apt_install__all_packages.j2`
  template from scratch to make it maintainable and expendable in 42 lines of
  straight Jinja2 ;-). [ypid]

- Implemented :any:`apt_install__conditional_whitelist_packages` previously
  known as ``apt__conditional_whitelist`` in ``debops.apt``. [ypid]

- Updated and fixed up metadata and copyright. [ypid]

- Small fixes in the documentation. [drybjed]

v0.1.0
------

*Released: 2016-05-26*

- Initial release. [drybjed]

