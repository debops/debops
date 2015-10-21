Changelog
=========

v0.1.1
------

*Released: 2015-10-21*

Great Scott!

- Fix a bug where, when ``atd`` management is disabled, on first install
  interval and load configuration variables were not initialized, and Ansible
  local facts template generation failed. Now in this case Ansible will use
  empty values. [drybjed]

v0.1.0
------

*Released: 2015-10-20*

- Initial release. [drybjed]

