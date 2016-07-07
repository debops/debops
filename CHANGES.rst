Changelog
=========

**debops.pki**

This project adheres to `Semantic Versioning <http://semver.org/>`_
and `human-readable changelog <http://keepachangelog.com/>`_.


Contributors
------------

- [drybjed] - `Maciej Delmanowski <https://github.com/drybjed/>`_  (role maintainer)
- [ypid] - `Robin Schneider <https://github.com/ypid/>`_


Unreleased
----------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.13...master>`_


v0.2.13 - 2016-07-07
--------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.12...v0.2.13>`_

Changed
~~~~~~~

- Update the Changelog with links to change diffs on GitHub. [drybjed]

- Include the ``COPYRIGHT`` file in the RST documentation. [drybjed]

- Update the ``.travis.yml`` configuration file. [drybjed]


v0.2.12 - 2016-07-06
--------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.11...v0.2.12>`_

Changed
~~~~~~~

- The session token is now generated using ``sha256`` hashing algorithm instead
  of ``MD5``. [drybjed]

- Move the copyright information to a ``COPYRIGHT`` file in the main directory.
  [drybjed]

- Move the example playbook to an external, separate file. [drybjed]


v0.2.11 - 2016-07-05
--------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.10...v0.2.11>`_

Added
~~~~~

- Ensure that highly sensitive files are not checked into version control when
  for example :program:`etckeeper` is used for tracking changes in :file:`/etc`.
  Note that sensitive files which are already tracked by version control will
  need to be manually deleted from version control history!
  Refer to :envvar:`pki_vcs_ignore_patterns_role` for more details. [ypid]

Changed
~~~~~~~

- Convert Changelog to the new format. [drybjed]

Fixed
~~~~~

- The PKI session token is now generated once for all hosts, by delegating the
  task to Ansible Controller. This fixes a bug with Ansible Playbook runs on
  multiple hosts at once, where only one host would receive the signed
  certificates at a time. [drybjed]


v0.2.10 - 2016-06-14
--------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.9...v0.2.10>`_

Changed
~~~~~~~

- Documentation fixes and improvements. Made variables hyperlinks using the
  `any` role in Sphinx which also ensures that variables which the
  documentation refers to actually exist. [ypid]

- Assert that required dependencies are met. [ypid]

- Use ``pki_ca_library`` variable to select correct crypto library for
  assertion. [drybjed]

- Don't assert crypto library version or ``bash`` version on Ansible Controller
  if no internal Certificate Authority is enabled. In this case they are not
  relevant for ``debops.pki`` operation. [drybjed]


v0.2.9 - 2016-06-01
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.8...v0.2.9>`_

Added
~~~~~

- Expose the list with order of authority preference used by a PKI realm to
  select active valid certificate in role default variables. [drybjed]

- Add support for creation of self-signed certificates when internal CA is
  disabled. This enables proper operation of other services like :program:`nginx`,
  which can then be used to request and authenticate ACME certificates.
  [drybjed]


v0.2.8 - 2016-05-05
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.7...v0.2.8>`_

Added
~~~~~

- Add support for setting filesystem ACL entries for private directories and
  files. [drybjed]

Changed
~~~~~~~

- Include realms defined in :any:`pki_default_realms` in tasks that copy files
  from Ansible Controller depending on an Ansible inventory group. [drybjed]


v0.2.7 - 2016-05-03
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.6...v0.2.7>`_

Changed
~~~~~~~

- Documentation improvements. Fixed examples, spelling, grammar and Sphinx inline
  syntax. [ypid]

- Don’t rely on the value of the special variable ``omit`` for having a high
  enough entropy (or any entropy at all) to use it as PKI session token.
  Although usage of the ``omit`` variable for this use case is quite creative
  and has been suggested by one of the Ansible core developers, it is believed
  that this does not meet the quality and maintainability standards of the
  DebOps project. Now the ``random`` Jinja filter is used as random source
  which is more explicit, has a proper entropy and is less hacky. [ypid]

- Honor the value of ``ansible_local.root.lib``. Previously, using another
  value than :file:`/usr/local/lib` would have broken the role. [ypid]

- Only use ``pki_fact_lib_path`` inside of quotes as this value could contain
  whitespace characters. [ypid]


v0.2.6 - 2016-04-12
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.5...v0.2.6>`_

Changed
~~~~~~~

- Convert ACME intermediate certificate from DER to PEM format automatically.
  [drybjed]

- Make sure that role works with older ``debops.nginx`` deployments, which
  didn't support ACME integration. [drybjed]


v0.2.5 - 2016-03-02
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.4...v0.2.5>`_

Changed
~~~~~~~

- Don't run :program:`pki-authority` script on Ansible Controller if list of
  :any:`pki_authorities` is not defined. [drybjed]


v0.2.4 - 2016-02-21
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.3...v0.2.4>`_

Changed
~~~~~~~

- Use a more portable "shebang" string in Bash scripts. [drybjed]

- Provide a portable ``dnsdomainname`` alternative function which works on
  operating systems without the former command present. [drybjed]

- Use short :command:`hostname -f` argument for portability. [drybjed]

- Update support for ``subjectAltName`` extension in certificates. Currently
  only IP addresses, DNS records, URI paths and emails are supported. [drybjed]

- Document ``pki_realms`` lists. [drybjed]

- Redesign the :file:`secret/pki/ca-certificates/` directory. It's now based on
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
  :program:`pki-realm` script will now check the signed certificate for the "CA
  Issuers" URI and download the certificate using it. The URI is stored and
  used later to check if the new certificate has the same or different URI, to
  not download the intermediate certificate every time the :program:`pki-realm` script
  is run. [drybjed]

- Slight changes in certificate chaining logic, to ensure that when
  certificates are changed, all generated chained certificate files are
  correctly updated. [drybjed]


v0.2.3 - 2016-02-08
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.2...v0.2.3>`_

Changed
~~~~~~~

- Replace the example hook script with something that actually works. [drybjed]

- Fix deprecation warnings in Ansible 2.1.0. [drybjed]


v0.2.2 - 2016-02-03
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.1...v0.2.2>`_

Added
~~~~~

- Add support for Diffie-Hellman parameters appended to certificate chains. DHE
  parameters are managed by ``debops.dhparam`` Ansible role. [drybjed]

Changed
~~~~~~~

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

- Do not create a :program:`cron` task when support for PKI is disabled on a host.
  [drybjed]


v0.2.1 - 2016-02-01
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.2.0...v0.2.1>`_

Changed
~~~~~~~

- Update old README with new documentation. [drybjed]


v0.2.0 - 2016-02-01
-------------------

`Compare changes <https://github.com/debops/ansible-pki/compare/v0.1.0...v0.2.0>`_

Changed
~~~~~~~

- Replace old ``debops.pki`` role with a new, redesigned version. Some
  additional code, variable cleanup and documentation is still missing, but
  role is usable at this point. [drybjed]


v0.1.0 - 2016-01-04
-------------------

Added
~~~~~

- Add Changelog. [drybjed]

- Blacklist CNNIC Root CA following the `Google decision to remove CNNIC`_ from
  their Root CA store. [drybjed]

.. _Google decision to remove CNNIC: https://security.googleblog.com/2015/03/maintaining-digital-certificate-security.html

- Add support for managing the list of active Root CA Certificates in
  :file:`/etc/ca-certificates.conf`. Current set of active Root CA Certificates is
  preserved. [drybjed]

- Add a way to copy arbitrary files from Ansible Controller to remote host PKI
  directories. [drybjed]

- Expose ``ansible_fqdn`` variable as :any:`pki_fqdn` so that it can be overridden
  if necessary. [drybjed]

Changed
~~~~~~~

- Reorder Changelog entries. [drybjed]

Removed
~~~~~~~

- Remove Diffie-Hellman parameter support from the role, it's now managed by
  a separate ``debops.dhparam`` Ansible role. Existing hosts won't be affected.
  [drybjed]

