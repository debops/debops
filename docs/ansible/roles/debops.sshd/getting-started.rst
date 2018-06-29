Getting started
===============

.. contents::
   :local:

Useful variables
----------------

This is a list of role variables which you most likely want to define in
Ansible inventory to customize OpenSSH server:

:envvar:`sshd__whitelist` / :envvar:`sshd__group_whitelist` / :envvar:`sshd__host_whitelist`
  Lists which contain IP addresses or CIDR subnets that are permitted to
  connect to OpenSSH without restrictions or firewall limits. Adding entries
  here will not impose additional restrictions, unlike using ``sshd__*_allow``
  lists.

:envvar:`sshd__known_hosts` / :envvar:`sshd__group_known_hosts` / :envvar:`sshd__host_known_hosts`
  Here you can add lists of FQDN hostnames which should be added to systemwide
  :file:`/etc/ssh/ssh_known_hosts` file. For example, setting::

      sshd__known_hosts: [ 'github.com' ]

  will add GitHub SSH fingerprint and allow you to clone git repositories over
  SSH with proper host authentication, without the need to ignore host
  fingerprints.

:envvar:`sshd__authorized_keys_lookup`
  Boolean. If ``True``, role will enable lookup of SSH public keys in external
  authentication databases, like LDAP. This might require additional
  configuration using ``sshd__ldap_*`` variables.

  LDAP key lookup depends on system-wide LDAP configuration in
  :file:`/etc/ldap/ldap.conf`, which can be performed (at the moment) using
  :ref:`debops.auth` role.

Example inventory
-----------------

``debops.sshd`` role is part of the :file:`common.yml` DebOps playbook. It will be
executed automatically on every host managed by DebOps.

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.sshd`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/sshd.yml
   :language: yaml

Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::sshd``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``role::sshd:config``
  Execute tasks related to ``sshd`` configuration file.

``role::sshd:known_hosts``
  Scan specified host fingerprints and add them to system-wide ``known_hosts``.
