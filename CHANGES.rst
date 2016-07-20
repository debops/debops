Changelog
=========

**debops.docker**

`debops.docker master`_ - unreleased
------------------------------------

Changed
~~~~~~~
- Update documentation and Changelog. [tallandtree]

- Rename all role variables from ``docker_*`` to ``docker__*`` to move them into
  their own namespace. [tallandtree]

- ``*.changed`` is changed to ``*|changed`` to ensure correct variable type resolution by Ansible 

v0.1.2
------

*Released: 2015-12-19*

- Add a default list variable which can be used to open additional ports in the
  firewall for Docker-related services. [drybjed]

- Create :file:`/etc/systemd/system` directory if not present for the Docker
  systemd unit file. [drybjed]

v0.1.1
------

*Released: 2015-12-13*

- Remove hard role dependencies and move additional role configuration to
  default variables. Ansible playbook can use this configuration to set up
  firewall rules and reserve ports in :file:`/etc/services`. [drybjed]

- Check if ``ansible_ssh_user`` contains a value before adding the default user
  to ``docker`` group, otherwise use name of the user account running the
  Ansible playbook. [drybjed]

v0.1.0
------

*Released: 2015-09-06*

- Initial release. [drybjed]

