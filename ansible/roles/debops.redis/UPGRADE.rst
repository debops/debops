.. _redis__ref_upgrade_nodes:

Upgrade notes
=============

The upgrade notes only describe necessary changes that you might need to make
to your setup in order to use a new role release. Refer to the
:ref:`redis__ref_changelog` for more details about what has changed.

From v0.1.0 to v0.2.0
---------------------

All inventory variables have been renamed so you will need to update your
inventory. Check the variables in :file:`defaults/main.yml` file to see the changed
names.

The Redis Server and Sentinel parameters are not configured in separate default
variables anymore - instead, each one uses a set of YAML dictionary variables
to hold the configuration. Redis Server can be configured on all levels of the
Ansible inventory (all, group, host), Redis Sentinel can only be configured
globally.

Redis requires an authentication by a password before the applications can use it.
The password is accessible either via Ansible local facts (usable by other
Ansible roles), or using the ``redis-password`` command (usable by users
included in the ``redis-auth`` UNIX group). If you store the password in
a configuration file, make sure that only specific user or group can read it;
otherwise it can be read by untrusted users and the security will be broken.

Support for Debian Wheezy and SysVinit is removed, the role relies on systemd units
instead.

The Redis Server and Sentinel configuration files have been reorganized.
The role most likely will not work with existing installations. Clean reinstall
is strongly recommended.
