Getting started
===============

.. contents::
   :local:

Useful variables
----------------

This is a list of role variables which your most likely want to define in
Ansible inventory to customize OpenSSH server:

``sshd_whitelist`` / ``sshd_group_whitelist`` / ``sshd_host_whitelist``
  Lists which contain IP addresses or CIDR subnets that are permitted to
  connect to OpenSSH without restrictions or firewall limits. Adding entries
  here will not impose additional restrictions, unlike using ``sshd_*_allow``
  lists.

``sshd_known_hosts`` / ``sshd_group_known_hosts`` / ``sshd_host_known_hosts``
  You can add here lists of FQDN hostnames which should be added to systemwide
  ``/etc/ssh/ssh_known_hosts`` file. For example, setting ``sshd_known_hosts:
  [ 'github.com' ]`` will add GitHub SSH fingerprint and allow you to clone git
  repositories over SSH with proper host authentication, without need to ignore
  host fingerprints.

``sshd_authorized_keys_lookup``
  Boolean. If ``True``, role will enable lookup of SSH public keys in external
  authentication databases, like LDAP. This might require additional
  configuration using ``sshd_ldap_*`` variables.

  LDAP key lookup depends on system-wide LDAP configuration in
  ``/etc/ldap/ldap.conf``, which can be performed (at the moment) using
  ``debops.auth`` role.

Example inventory
-----------------

``debops.sshd`` role is part of the ``common.yml`` DebOps playbook. It will be
executed automatically on every host managed by DebOps.

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after host is first
configured to speed up playbook execution, when you are sure that most of the
configuration has not been changed.

Available role tags:

``role::sshd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::sshd:config``
  Execute tasks related to ``sshd`` configuration file.

``role::sshd:known_hosts``
  Scan specified host fingerprints and add them to system-wide ``known_hosts``.

