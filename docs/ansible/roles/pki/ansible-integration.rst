Ansible integration
===================

The ``debops.pki`` role creates Ansible local facts on each managed remote
host. These local facts can be used by other Ansible roles as an idempotent
source of PKI-related configuration – they should be accessible from any
playbook executed on that host without the requirement of the ``debops.pki``
role being a part of it or a role dependency.

The local facts are saved in ``ansible_local.pki.*`` namespace. List of
available facts:

``ansible_local.pki.enabled``
  Boolean. Can be used to determine if PKI is enabled on a given host. This
  doesn't mean that a particular PKI realm has a correctly configured set of
  private keys and certificates.

``ansible_local.pki.acme``
  Boolean. Specifies if an ACME environment is enabled on a given host, which
  means that the :program:`acme-tiny` script is installed and any PKI realm
  that is not configured otherwise will try to register an ACME certificate.

``ansible_local.pki.internal``
  Boolean. Specifies that PKI realms configured on a given host will request
  certificates in internal Certificate Authority.

``ansible_local.pki.path``
  Directory where PKI realms are located, by default :file:`/etc/pki/realms/`.

``ansible_local.pki.hooks``
  Directory where PKI hooks are located, by default :file:`/etc/pki/hooks/`.

``ansible_local.pki.realm``
  Default server realm name configured for this system, should be used as the
  provider of private key and certificate for a given service.

``ansible_local.pki.ca_realm``
  Default client realm name configured for this system, should be used as the
  provider of the CA certificate for a given service.

``ansible_local.pki.known_realms``
  List which contains names of all PKI realms that might be present on a given
  remote host. Contents of the list are never removed, only appended. This list
  can be used to check on the Ansible playbook/role level if a given PKI realm
  is available to be used.

The facts listed below are currently static, but are planned to be used in the
future for better control over PKI realm directory structure:

:file:`ansible_local.pki.crt`
  Name of the default certificate symlink located in the PKI realm main
  directory.

``ansible_local.pki.key``
  Name of the default private key symlink located in the PKI realm main
  directory.

:file:`ansible_local.pki.pem`
  Name of the default private key and certificate bundle symlink located in the
  PKI realm main directory.

``ansible_local.pki.ca``
  Name of the default CA certificate symlink located in the PKI realm main
  directory.

``ansible_local.pki.trusted``
  Name of the trusted CA chain symlink located in the PKI realm main directory.

