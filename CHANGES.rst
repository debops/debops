Changelog
=========

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

