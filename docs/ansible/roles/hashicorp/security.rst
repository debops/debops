.. _hashicorp__ref_security:

debops.hashicorp security considerations
========================================

.. include:: ../../../includes/global.rst

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

The `Debian Go Packaging Team`_
maintains source and binary packages of selected HashiCorp_ applications in the
Debian Software Repository. The Debian packages for different applications
should be the preferred installation method when they are readily available on
the Debian Stable release.

The ``debops.hashicorp`` role is written in the belief that the verified and
authenticated access to the upstream versions of HashiCorp_ applications, even
though installed using binary packages, can still be useful, for example to
provide secure installation path to the software not packaged in Debian.


Software sources
----------------

The HashiCorp_ company publishes the source code of
each application on GitHub, in the `hashicorp organization <https://github.com/hashicorp/>`_.
Each release is tagged using :command:`git` tags. Each tag is signed by the HashiCorp_
OpenPGP key.

The process that HashiCorp_ uses to build binary Go packages from the sources on
GitHub and deploy them on their release page is currently unpublished.

It is unknown if the HashiCorp_ application builds are reproducible and can be
independently verified.

Each released version of an application is published on the HashiCorp_
`release page <https://releases.hashicorp.com/>`__. The applications are published
as versioned ``.zip`` archives, each archive containing one or more Go binaries.
Each archive file is hashed using SHA256 algorithm. Hashes of all provided
files are stored in a separate file which is signed by the HashiCorp_ OpenPGP key.


HashiCorp OpenPGP key
---------------------

The `HashiCorp Security Policy`_ page contains information about the OpenPGP
key used to sign the application releases. The OpenPGP key fingerprint of the
key used by HashiCorp_ is:

.. code-block:: none

   91A6 E7F8 5D05 C656 30BE F189 5185 2D87 348F FC4C

The HashiCorp_ OpenPGP key is published on the keybase.io_ website, on the
`hashicorp account <https://keybase.io/hashicorp>`_. The key is tracked by
several other users of the site.

The HashiCorp_ OpenPGP key is published in the `SKS OpenPGP keyserver pool`_
and can be imported from there using the :command:`gpg` command:

.. code-block:: console

   user@host:~$ gpg --keyserver hkp://pool.sks-keyservers.net \
                    --recv-key 91A6E7F85D05C65630BEF18951852D87348FFC4C


Software installation procedure
-------------------------------

The steps outlined below describe the method used by the ``debops.hashicorp``
role to verify and install the HashiCorp_ applications selected by the user or
another Ansible role:

- The ``debops.hashicorp`` Ansible role creates a separate, unprivileged system
  group and UNIX user account, by default both named ``hashicorp``. The account
  does not provide shell access and uses :file:`/usr/sbin/nologin` shell by
  default.

  Additionally, several directories owned by the new user account are created
  to provide location to unpack the verified archives in preparation for the
  installation.

- The ``hashicorp`` user account imports the HashiCorp_ OpenPGP key from the
  OpenPGP keyserver network, by default using one of the SHS Keyservers.

- The ``hashicorp`` user account downloads the necessary files from the
  HashiCorp_ release page over the HTTPS protocol. These files include: binary
  archive files, files containing SHA256 hashes of the provided files, files
  containing OpenPGP signatures of the hash files.

- The ``hashicorp`` user account verifies the signature of the SHA256 hash file
  against the HashiCorp_ OpenPGP key imported prior.

- If the signature verification passed, the ``hashicorp`` user compares the SHA
  256 hashes provided in the signed file against the downloaded binary
  archives.

- If the hash verification was successful, the ``hashicorp`` user account
  unpacks the binary archives of the HashiCorp_ applications to separate
  directories created prior.

- The ``root`` user account installs the unpacked application binaries to the
  specified directory (by default :file:`/usr/local/bin`) with ``root:root`` owner
  and group. Additional files required by the Consul Web UI are copied to
  specified web root directory (by default :file:`/srv/www/consul/sites/public/`)
  when the Consul Web UI is enabled.

All of the downloaded and unpacked files are left intact to allow for idempotent
operation and verification.
