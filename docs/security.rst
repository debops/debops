.. _hashicorp__ref_security:

debops.hashicorp security considerations
========================================

.. include:: includes/all.rst

.. contents::
   :local:


Role security guidelines
------------------------

Because the ``debops.hashicorp`` role can be used to install binary Go
applications on production systems, it was designed to check and validate the
archives used for application deployment against a known Trust Path. This
document explains the steps taken by the role to authenticate and verify the
installed software.


HashiCorp applications in Debian Software Repository
----------------------------------------------------

The `Debian Go Packaging Team <https://qa.debian.org/developer.php?login=pkg-go-maintainers%40lists.alioth.debian.org>`_
maintains source and binary packages of selected HashiCorp applications in the
Debian Software Repository. The Debian packages for different applications
should be the preferred installation method when they are readily available on
the Debian Stable release.

The ``debops.hashicorp`` role is written in the belief that the verified and
authenticated access to the upstream versions of HashiCorp applications, even
though installed using binary packages, can still be useful, for example to
provide secure installation path to the software not packaged in Debian.


Software sources
----------------

The `HashiCorp <https://hashicorp.com/>`_ company publishes the source code of
each application on GitHub, in the `hashicorp organization <https://github.com/hashicorp/>`_.
Each release is tagged using ``git`` tags. Each tag is signed by the HashiCorp
OpenPGP key.

The process that HashiCorp uses to build binary Go packages from the sources on
GitHub and deploy them on their release page is currently unpublished.

It is unknown if the HashiCorp application builds are reproducible and can be
independently verified.

Each released version of an application is published on the HashiCorp
`release page <https://releases.hashicorp.com/>`_. The applications are published
as versioned ``.zip`` archives, each archive containing one or more Go binaries.
Each archive file is hashed using SHA256 algorithm. Hashes of all provided
files are stored in a separate file which is signed by the HashiCorp OpenPGP key.


HashiCorp OpenPGP key
---------------------

The `HashiCorp Security Policy <https://www.hashicorp.com/security.html>`_ page
contains information about the OpenPGP key used to sign the application
releases. The OpenPGP key fingerprint of the key used by HashiCorp is:

.. code-block:: none

   91A6 E7F8 5D05 C656 30BE F189 5185 2D87 348F FC4C

The HashiCorp OpenPGP key is published on the
`keybase.io <https://keybase.io>`_ website, on the
`hashicorp account <https://keybase.io/hashicorp>`_. The key is tracked by
several other users of the site.

The HashiCorp OpenPGP key is published in the `SKS OpenPGP keyserver pool <https://sks-keyservers.net/>`_
and can be imported from there using the ``gpg`` command:

.. code-block:: console

   user@host:~$ gpg --keyserver hkp://pool.sks-keyservers.net \
                    --recv-key 91A6E7F85D05C65630BEF18951852D87348FFC4C


Software installation procedure
-------------------------------

The steps outlined below describe the method used by the ``debops.hashicorp``
role to verify and install the HashiCorp applications selected by the user or
another Ansible role:

- The ``debops.hashicorp`` Ansible role creates a separate, unprivileged system
  group and UNIX user account, by default both named ``hashicorp``. The account
  does not provide shell access and uses ``/usr/sbin/nologin`` shell by
  default.

  Additionally, several directories owned by the new user account are created
  to provide location to unpack the verified archives in preparation for the
  installation.

- The ``hashicorp`` user account imports the HashiCorp OpenPGP key from the
  OpenPGP keyserver network, by default using one of the SHS Keyservers.

- The ``hashicorp`` user account downloads the necessary files from the
  HashiCorp release page over the HTTPS protocol. These files include: binary
  archive files, files containing SHA256 hashes of the provided files, files
  containing OpenPGP signatures of the hash files.

- The ``hashicorp`` user account verifies the signature of the SHA256 hash file
  against the HashiCorp OpenPGP key imported prior.

- If the signature verification passed, the ``hashicorp`` user compares the SHA
  256 hashes provided in the signed file against the downloaded binary
  archives.

- If the hash verification was successful, the ``hashicorp`` user account
  unpacks the binary archives of the HashiCorp applications to separate
  directories created prior.

- The ``root`` user account installs the unpacked application binaries to the
  specified directory (by default ``/usr/local/bin``) with ``root:root`` owner
  and group. Additional files required by the Consul Web UI are copied to
  specified web root directory (by default ``/srv/www/consul/sites/public/``)
  when the Consul Web UI is enabled.

All of the downloaded and unpacked files are left intact to allow for idempotent
operation and verification.
