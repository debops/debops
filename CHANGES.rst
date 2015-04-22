Changelog
=========

v0.1.0
------

*Unreleased*

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

