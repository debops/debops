Changelog
=========

.. include:: includes/all.rst

**debops.pki**

This project adheres to `Semantic Versioning <http://semver.org/spec/v2.0.0.html>`__
and `human-readable changelog <http://keepachangelog.com/en/1.0.0/>`__.

The current role maintainer_ is drybjed_.


`debops.pki master`_ - unreleased
----------------------------------

.. _debops.pki master: https://github.com/debops/ansible-pki/compare/v0.2.14...master

Added
~~~~~

- Add custom pre and post task hooks to allow more flexibility with PKI
  management. [muelli_]

- Support to change or disable CRL and OCSP for PKI authorities using
  ``item.crl`` and ``item.ocsp``. [ypid_]

- Use X.509 Name Constraints to limit PKI authorities to ``item.domain`` by default.
  This greatly reduces the damage that a compromised PKI authority could do
  (which is trusted by the cluster by default).
  Previously, any CA managed by ``debops.pki`` could happily issue certificates
  for any domain and clients would accept them which is probably not what you want.
  Use ``item.name_constraints`` if you want to change the default.
  Note that this new default is only effective for newly created CAs.
  Refer to `A Web PKI x509 certificate primer <https://developer.mozilla.org/en-US/docs/Mozilla/Security/x509_Certificates>`_
  for details. [ypid_]

- Support to change the number of days a selfsigned certificate will be valid
  for by exposing the ``selfsigned_sign_days`` option for :envvar:`pki_realms`. [ypid_]

Fixed
~~~~~

- Fix Ansible 2.2 deprecation warnings which requires Ansible 2.2 or higher.
  Support for older Ansible versions is dropped. [brzhk]

- Sign certificate requests on Ansible Controller only for hosts that have
  their Ansible facts gathered. [drybjed_]

- pki-realm: Fix ``selfsigned_sign_days`` config option which was ignored previously.
  This did not have any effect for users of the role because changing that
  setting was not supported previously either. [ypid_]


`debops.pki v0.2.14`_ - 2016-11-21
----------------------------------

.. _debops.pki v0.2.14: https://github.com/debops/ansible-pki/compare/v0.2.13...v0.2.14

Added
~~~~~

- Added :envvar:`pki_create_acme_challenge_dir`. [muelli_]

- Reintroduce the possibility to configure RSA key sizes using
  :envvar:`pki_realm_key_size` (realms) and ``pki_ca_*_key_size`` (CAs) which
  was removed in v0.2.0. [ypid_]

- Silently ignore empty elements in ``subject`` and ``acme_subject`` lists.
  This can come in handy to create the certificate subjects using Jinja in the
  Ansible inventory. [ypid_]

- Allow to disable CA certificates download for the different levels. [ypid_]

- Added :envvar:`pki_system_ca_certificates_download_all_hosts_force`. [ypid_]

- Gather and expose OpenSSL and GnuTLS versions in Ansible local facts. [ypid_]

Changed
~~~~~~~

- Change the method that Bash scripts use to compare the version numbers for
  a more reliable one. [drybjed_]

- Documentation improvements. [ypid_]

- Remove the ``www`` subdomain from list of default ACME subdomains. This
  should make configuration of ACME certificates easier. [drybjed_]

- Make sure that the ``domain`` PKI realm by default adds the host FQDN to the
  list of Subject Alt Names of a certificate. This should solve an issue with
  some software which cannot deal with wildcard hostnames properly. [drybjed_]

Fixed
~~~~~

- Fix an error where certain versions of GnuTLS ``certtool`` did not support
  the "URI" SubjectAltName which resulted in an abort and certificate requests
  not being generated correctly. The "URI" SANs will only be added when correct
  version of the ``certtool`` is available. [drybjed_]

- Fix an issue where ACME certificate requests were not performed correctly on
  Ubuntu hosts due to the default ``umask`` setting of the user accounts being
  ``0007``, which resulted in the web server not being able to serve ACME
  challenge responses. Now, correct ``umask`` will be set for the :program:`acme-tiny`
  script, so that ACME responses are world-readable. [drybjed_]

- Fix an error in :program:`pki-authority` script which invoked a Python print call
  that was unsupported in modern Python versions, the call is now supported
  on both 2.x and 3.x. [yuvadm_]

- Don’t use ``MD5`` or other hash functions to sanitize STDOUT of programs for later
  comparison when a simple ``base64`` encoding is enough. [ypid_]

- Also run :program:`pki-realm new-realm` against realms with disabled internal
  CA. [ypid_]

- Reviewed the role. Fixed potential shell script issues reported by
  :command:`shellcheck` and added CI tests using :command:`shellcheck`. [ypid_]

- Use the group id instead of group names (from :command:`id -gn` to
  :command:`id -g`) in :program:`pki-realm` and :program:`pki-authority` to
  cope with group names with spaces which can happen when LDAP is used. [zpfvo_]


`debops.pki v0.2.13`_ - 2016-07-07
----------------------------------

.. _debops.pki v0.2.13: https://github.com/debops/ansible-pki/compare/v0.2.12...v0.2.13

Changed
~~~~~~~

- Update the Changelog with links to change diffs on GitHub. [drybjed_]

- Include the ``COPYRIGHT`` file in the RST documentation. [drybjed_]

- Update the :file:`.travis.yml` configuration file. [drybjed_]


`debops.pki v0.2.12`_ - 2016-07-06
----------------------------------

.. _debops.pki v0.2.12: https://github.com/debops/ansible-pki/compare/v0.2.11...v0.2.12

Changed
~~~~~~~

- The session token is now generated using ``SHA-256`` hashing algorithm instead
  of ``MD5``. [drybjed_]

- Move the copyright information to a ``COPYRIGHT`` file in the main directory.
  [drybjed_]

- Move the example playbook to an external, separate file. [drybjed_]


`debops.pki v0.2.11`_ - 2016-07-05
----------------------------------

.. _debops.pki v0.2.11: https://github.com/debops/ansible-pki/compare/v0.2.10...v0.2.11

Added
~~~~~

- Ensure that highly sensitive files are not checked into version control when
  for example :program:`etckeeper` is used for tracking changes in :file:`/etc`.
  Note that sensitive files which are already tracked by version control will
  need to be manually deleted from version control history!
  Refer to :envvar:`pki_vcs_ignore_patterns_role` for more details. [ypid_]

Changed
~~~~~~~

- Convert Changelog to the new format. [drybjed_]

Fixed
~~~~~

- The PKI session token is now generated once for all hosts, by delegating the
  task to Ansible Controller. This fixes a bug with Ansible Playbook runs on
  multiple hosts at once, where only one host would receive the certificates at
  a time. [drybjed_]


`debops.pki v0.2.10`_ - 2016-06-14
----------------------------------

.. _debops.pki v0.2.10: https://github.com/debops/ansible-pki/compare/v0.2.9...v0.2.10

Changed
~~~~~~~

- Documentation fixes and improvements. Made variables hyperlinks using the
  `any` role in Sphinx which also ensures that variables which the
  documentation refers to actually exist. [ypid_]

- Assert that required dependencies are met. [ypid_]

- Use ``pki_ca_library`` variable to select correct crypto library for
  assertion. [drybjed_]

- Don't assert crypto library version or ``bash`` version on Ansible Controller
  if no internal Certificate Authority is enabled. In this case they are not
  relevant for ``debops.pki`` operation. [drybjed_]


`debops.pki v0.2.9`_ - 2016-06-01
---------------------------------

.. _debops.pki v0.2.9: https://github.com/debops/ansible-pki/compare/v0.2.8...v0.2.9

Added
~~~~~

- Expose the list with order of authority preference used by a PKI realm to
  select active valid certificate in role default variables. [drybjed_]

- Add support for creation of self-signed certificates when internal CA is
  disabled. This enables proper operation of other services like :program:`nginx`,
  which can then be used to request and authenticate ACME certificates.
  [drybjed_]


`debops.pki v0.2.8`_ - 2016-05-05
---------------------------------

.. _debops.pki v0.2.8: https://github.com/debops/ansible-pki/compare/v0.2.7...v0.2.8

Added
~~~~~

- Add support for setting filesystem ACL entries for private directories and
  files. [drybjed_]

Changed
~~~~~~~

- Include realms defined in :envvar:`pki_default_realms` in tasks that copy files
  from Ansible Controller depending on an Ansible inventory group. [drybjed_]


`debops.pki v0.2.7`_ - 2016-05-03
---------------------------------

.. _debops.pki v0.2.7: https://github.com/debops/ansible-pki/compare/v0.2.6...v0.2.7

Changed
~~~~~~~

- Documentation improvements. Fixed examples, spelling, grammar and Sphinx inline
  syntax. [ypid_]

- Don’t rely on the value of the special variable ``omit`` for having a high
  enough entropy (or any entropy at all) to use it as PKI session token.
  Although usage of the ``omit`` variable for this use case is quite creative
  and has been suggested by one of the Ansible core developers, it is believed
  that this does not meet the quality and maintainability standards of the
  DebOps project. Now the ``random`` Jinja filter is used as random source
  which is more explicit, has a proper entropy and is less hacky. [ypid_]

- Honor the value of ``ansible_local.root.lib``. Previously, using another
  value than :file:`/usr/local/lib` would have broken the role. [ypid_]

- Only use ``pki_fact_lib_path`` inside of quotes as this value could contain
  whitespace characters. [ypid_]


`debops.pki v0.2.6`_ - 2016-04-12
---------------------------------

.. _debops.pki v0.2.6: https://github.com/debops/ansible-pki/compare/v0.2.5...v0.2.6

Changed
~~~~~~~

- Convert ACME intermediate certificate from DER to PEM format automatically.
  [drybjed_]

- Make sure that role works with older debops.nginx_ deployments, which
  didn't support ACME integration. [drybjed_]


`debops.pki v0.2.5`_ - 2016-03-02
---------------------------------

.. _debops.pki v0.2.5: https://github.com/debops/ansible-pki/compare/v0.2.4...v0.2.5

Changed
~~~~~~~

- Don't run :program:`pki-authority` script on Ansible Controller if list of
  :envvar:`pki_authorities` is not defined. [drybjed_]


`debops.pki v0.2.4`_ - 2016-02-21
---------------------------------

.. _debops.pki v0.2.4: https://github.com/debops/ansible-pki/compare/v0.2.3...v0.2.4

Changed
~~~~~~~

- Use a more portable "shebang" string in Bash scripts. [drybjed_]

- Provide a portable ``dnsdomainname`` alternative function which works on
  operating systems without the former command present. [drybjed_]

- Use short :command:`hostname -f` argument for portability. [drybjed_]

- Update support for ``subjectAltName`` extension in certificates. Currently
  only IP addresses, DNS records, URI paths and emails are supported. [drybjed_]

- Document ``pki_realms`` lists. [drybjed_]

- Redesign the :file:`secret/pki/ca-certificates/` directory. It's now based on
  Ansible inventory groups and allows distribution of CA certificates to all
  hosts, specific host groups, or specific hosts. [drybjed_]

- Don't update symlinks if the target is correct. [drybjed_]

- Split file signature creation and verification. This allows checking if the
  file signature is correct without updating it, so that it can be performed at
  different stages of the script. [drybjed_]

- Make sure that request generation works without subdomains and SANs present.
  [drybjed_]

- Automatically reset incomplete internal certificate requests.

  If a certificate does not exist in the realm and internal certificates
  are enabled, something must have gone wrong with the certificate signing. To
  make it easier, generated configuration file and CSR are removed so that they
  can be recreated further in the script with current session token and not
  rejected by the internal CA. [drybjed_]

- Change the way ACME intermediate CA certificate is downloaded.

  Instead of using a static URL to download an intermediate certificate,
  :program:`pki-realm` script will now check the certificate for the "CA
  Issuers" URI and download the certificate using it. The URI is stored and
  used later to check if the new certificate has the same or different URI, to
  not download the intermediate certificate every time the :program:`pki-realm` script
  is run. [drybjed_]

- Slight changes in certificate chaining logic, to ensure that when
  certificates are changed, all generated chained certificate files are
  correctly updated. [drybjed_]


`debops.pki v0.2.3`_ - 2016-02-08
---------------------------------

.. _debops.pki v0.2.3: https://github.com/debops/ansible-pki/compare/v0.2.2...v0.2.3

Changed
~~~~~~~

- Replace the example hook script with something that actually works. [drybjed_]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed_]


`debops.pki v0.2.2`_ - 2016-02-03
---------------------------------

.. _debops.pki v0.2.2: https://github.com/debops/ansible-pki/compare/v0.2.1...v0.2.2

Added
~~~~~

- Add support for Diffie-Hellman parameters appended to certificate chains. DHE
  parameters are managed by debops.dhparam_ Ansible role. [drybjed_]

Changed
~~~~~~~

- When an active authority directory is changed, correctly clean up files not
  present in the new authority directory and symlinks without existing targets.
  [drybjed_]

- Do not enable PKI support on remote hosts without defined domain. Without
  this applications try to use non-existent X.509 certificates and fail.
  [drybjed_]

- Make system PKI realm selection idempotent. Now, if another role changes the
  default system realm, running ``debops.pki`` role without that override will
  keep the realm specified in Ansible local facts. [drybjed_]

- Make sure that CA organization is non-empty. If a host domain is not
  configured correctly, hostname will be used instead. This makes some of the
  URLs in created CA certificates incorrect, but the ``debops.pki`` role works
  fine otherwise, and internal Certificate Authorities are easy to recreate
  with correct configuration. [drybjed_]

- Change the file tracked by the PKI realm creation task to be the realm
  private key instead of the certificate. This allows for realms that only
  contain Root CA certificates and does not create idempotency issues.
  [drybjed_]

- Do not create a :program:`cron` task when support for PKI is disabled on a host.
  [drybjed_]


`debops.pki v0.2.1`_ - 2016-02-01
---------------------------------

.. _debops.pki v0.2.1: https://github.com/debops/ansible-pki/compare/v0.2.0...v0.2.1

Changed
~~~~~~~

- Update old README with new documentation. [drybjed_]


`debops.pki v0.2.0`_ - 2016-02-01
---------------------------------

.. _debops.pki v0.2.0: https://github.com/debops/ansible-pki/compare/v0.1.0...v0.2.0

Changed
~~~~~~~

- Replace old ``debops.pki`` role with a new, redesigned version. Some
  additional code, variable cleanup and documentation is still missing, but
  role is usable at this point. [drybjed_]


debops.pki v0.1.0 - 2016-01-04
------------------------------

Added
~~~~~

- Add Changelog. [drybjed_]

- Blacklist CNNIC Root CA following the `Google decision to remove CNNIC`_ from
  their Root CA store. [drybjed_]

.. _Google decision to remove CNNIC: https://security.googleblog.com/2015/03/maintaining-digital-certificate-security.html

- Add support for managing the list of active Root CA Certificates in
  :file:`/etc/ca-certificates.conf`. Current set of active Root CA Certificates is
  preserved. [drybjed_]

- Add a way to copy arbitrary files from Ansible Controller to remote host PKI
  directories. [drybjed_]

- Expose ``ansible_fqdn`` variable as :envvar:`pki_fqdn` so that it can be overridden
  if necessary. [drybjed_]

Changed
~~~~~~~

- Reorder Changelog entries. [drybjed_]

Removed
~~~~~~~

- Remove Diffie-Hellman parameter support from the role, it's now managed by
  a separate debops.dhparam_ Ansible role. Existing hosts won't be affected.
  [drybjed_]
