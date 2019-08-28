Getting started
===============

.. contents::
   :local:

Changes from Debian defaults
----------------------------

The ``debops.sshd`` role will configure the OpenSSH server to lookup the client
hostnames in DNS by setting the ``UseDNS`` option to ``yes`` (the Debian and
upstream default is ``no``). This allows use of the DNS hostnames and domains
in the authorized keys files and PAM access control rules. DNS lookup can be
controlled using the :envvar:`sshd__use_dns` variable.

The role will divert the original :file:`/etc/pam.d/sshd` configuration file
and generate a new one, with PAM access control enabled and using the separate
:file:`/etc/security/access-sshd.conf` configuration file. The ACL rules are
defined in the :envvar:`sshd__pam_access__dependent_rules` variable and are
managed by the :ref:`debops.pam_access` Ansible role.

To disable the custom access control configuration, set the
:envvar:`sshd__pam_deploy_state` variable to ``absent``. The PAM access control
file will still be generated, but it will not be used by the ``sshd`` service.

Global root access
------------------

By default the :ref:`debops.pam_access` configuration restricts access to the
``root`` account to hosts on the same DNS domain, for security. This might
cause unintended lockouts if your Ansible Controller host is on a completely
different domain than the remote host.

To disable the restricted access and allow connections to the ``root`` account
from anywhere on the network, you can set in your Ansible inventory, for
example in :file:`ansible/inventory/group_vars/all/pam_access.yml` file:

.. code-block:: yaml

   pam_access__rules:

     - name: 'sshd'
       state: 'append'
       options:

         - name: 'allow-root'
           origins: 'ALL'

Then, you need to apply the changes to the configuration using the "context" of
the :ref:`debops.sshd` role, for example by executing the command:

.. code-block:: console

   debops service/sshd -l <host> --tags role::pam_access --diff

This command will apply the PAM access configuration defined by the
:ref:`debops.sshd` role with modifications from the inventory; they won't be
applied in other contexts of the :ref:`debops.pam_access` role is used in and
shouldn't affect other access lists.

You could also add subnets, domains or other origins instead of allowing access
from any host; refer to the :ref:`pam_access__ref_rules` for more details.

.. _sshd__ref_root_password:

Access to the ``root`` account via password
-------------------------------------------

The :ref:`debops.sshd` role checks if the :file:`/root/.ssh/authorized_keys`
file is present on the host, using Ansible local facts defined by the
:ref:`debops.root_account` role. If the file is present, we assume that the
sysadmin SSH keys are on the host, and password-based access to the ``root``
account is disabled by setting the ``PermitRootLogin`` option to
``without-password`` and the ``PasswordAuthentication`` option to ``no``.

If the SSH authorized keys file is not present, the host is assumed to not be
fully provisioned yet. The ``PermitRootLogin`` option as well as the
``PasswordAuthentication`` option will be set to ``yes`` to permit access to
the ``root`` account via SSH. Note that the default PAM access policy set in
the :envvar:`sshd__pam_access__dependent_rules` variable still applies and
access to the ``root`` account will be limited to hosts on the same DNS domain.

Alternatively, if the sysadmin accounts are configured using the
:ref:`debops.system_users` Ansible role, access to the ``root`` account via
password and password authentication will also be disabled.

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
  :ref:`debops.ldap` role.

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
