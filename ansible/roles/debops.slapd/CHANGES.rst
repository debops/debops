Changelog
=========

v0.1.0
------

*Unreleased*

- First release, add CHANGES.rst [drybjed]

- Change the default ``olcAccess`` rules to not allow users to modify all of
  their own attributes by default. Fixes `Debian Bug #761406`_. [drybjed]

.. _Debian Bug #761406: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=761406

- Move ``olcSecurity`` rules to role defaults, so that they can be easily
  overridden if necessary. [drybjed]

- Add a variable that specifies LDAP database backend that's in use. On Debian
  Wheezy it's set to ``hdb`` by default, on Debian Jessie and other
  distributions it's set to ``mdb`` by default. [drybjed]

- Add ``openssh-lpk`` LDAP schema for support of OpenSSH Public Key lookup in
  LDAP server. [drybjed]

- Add ACL entry ``ou=Machines,<domain>`` to allow easy integration with
  ``debops.auth`` role. This entry allows hosts that are registered in LDAP to
  read all entries in the database. [drybjed]

- Remove index numbers from LDAP Access Control Lists. They will be added
  dynamically by a lookup template during Ansible run. Old lists are detected
  and should work as intended. [drybjed]

- Change ``cn=admin,dc=...`` account path in ``secret/`` directory so that it
  is shared among all ``slapd`` hosts in the cluster. This will stop the
  password from being updated over and over in ``secret/ldap/`` directory (for
  other roles), however a tradeoff will be an error at initial creation of the
  password if multiple ``slapd`` hosts are run at once due to an Ansible
  ``lookup()`` conflict; this can be avoided by creating the initial
  configuration on one of the servers instead of all of them.

  This commit might change the LDAP administrator password, you need to update
  it elsewhere after the change. [drybjed]

- Move lookup template directory to ``templates/`` directory where Ansible v2
  expects these templates. Ansible v1 still looks in ``files/`` so symlink to
  the new directory is created there for the role to work on older Ansible
  version. [drybjed]

- Switch the Diffie-Hellman parameter file to the one managed by
  ``debops.dhparam`` Ansible role. [drybjed]

- Add more keys indexed by default. [drybjed]

- Convert the ACL entries into YAML text blocks. This makes modifications to
  the list easier and allows for better Jinja templating. [drybjed]

- Remove the Ansible role dependencies and move the firewall and TCP Wrappers
  configuration to default variables. It can be used by other roles through the
  playbooks. [drybjed]

- Update the support for encrypted connections and DebOps PKI. Role should now
  correctly detect that ``debops.pki`` hasn't been configured on a host and
  configure ``slapd`` only with plain connection support. You are advised to
  not use this mode in production environment. [drybjed]

- Change ``sudo`` task parameters to ``become``. [drybjed]

