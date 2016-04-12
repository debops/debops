Changelog
=========

v0.2.6
------

*Released: 2016-04-12*

- Convert ACME intermediate certificate from DER to PEM format automatically.
  [drybjed]

- Make sure that role works with older ``debops.nginx`` deployments, which
  didn't support ACME integration. [drybjed]

v0.2.5
------

*Released: 2016-03-02*

- Don't run ``pki-authority`` script on Ansible Controller if list of
  ``pki_authorities`` is not defined. [drybjed]

v0.2.4
------

*Released: 2016-02-21*

- Use a more portable "shebang" string in Bash scripts. [drybjed]

- Provide a portable ``dnsdomainname`` alternative function which works on
  operating systems without the former command present. [drybjed]

- Use short ``hostname -f`` argument for portability. [drybjed]

- Update support for ``subjectAltName`` extension in certificates. Currently
  only IP addresses, DNS records, URI paths and emails are supported. [drybjed]

- Document ``pki_realms`` lists. [drybjed]

- Redesign the ``secret/pki/ca-certificates/`` directory. It's now based on
  Ansible inventory groups and allows distribution of CA certificates to all
  hosts, specific host groups, or specific hosts. [drybjed]

- Don't update symlinks if the target is correct. [drybjed]

- Split file signature creation and verification. This allows checking if the
  file signature is correct without updating it, so that it can be performed at
  different stages of the script. [drybjed]

- Make sure that request generation works without subdomains and SANs present.
  [drybjed]

- Automatically reset incomplete internal certificate requests.

  If a signed certificate does not exist in the realm and internal certificates
  are enabled, something must have gone wrong with the certificate signing. To
  make it easier, generated configuration file and CSR are removed so that they
  can be recreated further in the script with current session token and not
  rejected by the internal CA. [drybjed]

- Change the way ACME intermediate CA certificate is downloaded.

  Instead of using a static URL to download an intermediate certificate,
  ``pki-realm`` script will now check the signed certificate for the "CA
  Issuers" URI and download the certificate using it. The URI is stored and
  used later to check if the new certificate has the same or different URI, to
  not download the intermediate certificate every time the ``pki-realm`` script
  is run. [drybjed]

- Slight changes in certificate chaining logic, to ensure that when
  certificates are changed, all generated chained certificate files are
  correctly updated. [drybjed]

v0.2.3
------

*Released: 2016-02-08*

- Replace the example hook script with something that actually works. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]

v0.2.2
------

*Released: 2016-02-03*

- Add support for Diffie-Hellman parameters appended to certificate chains. DHE
  parameters are managed by ``debops.dhparam`` Ansible role. [drybjed]

- When an active authority directory is changed, correctly clean up files not
  present in the new authority directory and symlinks without existing targets.
  [drybjed]

- Do not enable PKI support on remote hosts without defined domain. Without
  this applications try to use non-existent X.509 certificates and fail.
  [drybjed]

- Make system PKI realm selection idempotent. Now, if another role changes the
  default system realm, running ``debops.pki`` role without that override will
  keep the realm specified in Ansible local facts. [drybjed]

- Make sure that CA organization is non-empty. If a host domain is not
  configured correctly, hostname will be used instead. This makes some of the
  URLs in created CA certificates incorrect, but the ``debops.pki`` role works
  fine otherwise, and internal Certificate Authorities are easy to recreate
  with correct configuration. [drybjed]

- Change the file tracked by the PKI realm creation task to be the realm
  private key instead of the certificate. This allows for realms that only
  contain Root CA certificates and does not create idempotency issues.
  [drybjed]

- Do not create a ``cron`` task when support for PKI is disabled on a host.
  [drybjed]

v0.2.1
------

*Released: 2016-02-01*

- Update old README with new documentation. [drybjed]

v0.2.0
------

*Released: 2016-02-01*

- Replace old ``debops.pki`` role with a new, redesigned version. Some
  additional code, variable cleanup and documentation is still missing, but
  role is usable at this point. [drybjed]

v0.1.0
------

*Released: 2016-01-04*

- Add Changelog. [drybjed]

- Blacklist CNNIC Root CA following the `Google decision to remove CNNIC`_ from
  their Root CA store. [drybjed]

.. _Google decision to remove CNNIC: http://googleonlinesecurity.blogspot.com/2015/03/maintaining-digital-certificate-security.html

- Add support for managing the list of active Root CA Certificates in
  ``/etc/ca-certificates.conf``. Current set of active Root CA Certificates is
  preserved. [drybjed]

- Reorder Changelog entries. [drybjed]

- Add a way to copy arbitrary files from Ansible Controller to remote host PKI
  directories. [drybjed]

- Remove Diffie-Hellman parameter support from the role, it's now managed by
  a separate ``debops.dhparam`` Ansible role. Existing hosts won't be affected.
  [drybjed]

- Expose ``ansible_fqdn`` variable as ``pki_fqdn`` so that it can be overriden
  if necessary. [drybjed]

