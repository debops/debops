Changelog
=========

v0.1.1
------

*Released: 2015-11-30*

- New variable ``tinc_interface_auto`` wich controls if VPN interface will be
  started at boot time, and if Ansible will automatically manage it during
  playbook runs if any changes occur. [drybjed]

- Change the ``tinc_host_port`` type from Int to String, so that there are no
  issues in ``debops.ferm`` role. [drybjed]

- Fix wrong name of the variable in host template. [drybjed]

- Wrap the name of the VPN node and replace all hypens with underscores, which
  is a ``tinc`` requirement. [drybjed]

v0.1.0
------

*Released: 2015-05-20*

- Initial release. [drybjed]

