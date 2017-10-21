Changelog
=========

v0.1.3
------

*Released: 2016-02-08*

- Change the way the role detects admin user account. [drybjed]

- Fix the deprecation warning in Ansible 2.1.0. [drybjed]

v0.1.2
------

*Released: 2015-11-07*

- Change the way Ansible gets the default user account which is allowed to use
  ``atd`` to support changes introduced in Ansible v2. [drybjed]

v0.1.1
------

*Released: 2015-10-21*

Great Scott!

- Fix a bug where, when ``atd`` management is disabled, on first install
  interval and load configuration variables were not initialized, and Ansible
  local facts template generation failed. Now in this case Ansible will use
  empty values. [drybjed]

- Quick review and fixed spelling. [ypid]

v0.1.0
------

*Released: 2015-10-20*

- Initial release. [drybjed]

