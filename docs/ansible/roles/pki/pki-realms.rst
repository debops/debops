.. _pki_realms_structure:

PKI realms structure
====================

.. include:: ../../../includes/global.rst

The concept of PKI realms is designed to provide a standardized way for various
applications to access X.509 certificates and private keys. The management of
the keys and certificates is moved outside of the application into a fixed
directory and file structure, which other applications can access.

.. contents::
   :local:

PKI realm overview
------------------

A "PKI realm" is a placeholder name for a bundle of the private key, X.509
certificate and Root CA certificate. This bundle has a certain directory
structure, rules for naming files and what symlinks are present. It is designed
so that from the outside of the :ref:`debops.pki` role other Ansible roles, or
services they manage, have a standardized, uniform location where they can find
X.509 certificates and private keys.

In different guides that describe setting up TLS for different services like
webservers, mail servers, databases, etc.  the private keys and X.509
certificates are usually put in different directories - for example
:file:`/etc/nginx/ssl/`, :file:`/etc/postfix/certs/`, :file:`/etc/ssl/certs/`,
and so on. The :ref:`debops.pki` role turns this around by setting up an
uniform set of directories split into "PKI realms", so that a host can have
multiple sets of certificates, each for different purposes. Then, various
services can be configured to get the private key and certificate files from
those specific directories, including privileged access to the private keys
when needed.

PKI realms have a concept of multiple certificate authorities - there's one set
of private keys which can be signed by different CAs - internal CA, external
CA, ACME CA and self-signed when everything else is disabled. There can be an
"example.org" PKI realm which has certificates signed by both internal CA and
the Let's Encrypt CA (via ACME), and the :command:`pki-realm` script used to
manage the realms on the remote hosts will automatically switch between them
after checking the validity of their X.509 certificates.


The application view
--------------------

Different applications have different requirements for X.509 certificates and
private keys. Some of them support keys and certificates in separate files,
others require them combined in a single file. The PKI realm is designed to
support both schemes at once.

The realms are located in the :file:`/etc/pki/realms/` directory. Each realm is
contained in it's own subdirectory. By default a ``domain`` realm is configured
by the role, and it's simplified directory structure looks like this:

.. code-block:: none

   /etc/pki/realms/
   └── domain/
       ├── CA.crt
       ├── default.crt
       ├── default.key
       ├── default.pem
       └── trusted.crt

Each of these symlinks point to a file contained in another subdirectory (see
the next section). The contents of these files are:

:file:`CA.crt`
  This is the "trust anchor" or Root Certificate Authority certificate used by
  the application to check the validity of client certificates. This file is
  publicly readable.

  :file:`CA.crt` may contain a CA certificate different than the one that issued
  the server certificate. In this case, this can be used to have separate
  client and server Certificate Authorities.

:file:`default.crt`
  This is the server certificate with optionally bundled Intermediate
  Certificate Authorities. It is sent to the clients during connection
  establishment by the application. This file is publicly readable.

:file:`default.key`
  This is the server private key. It's readable only by the ``root`` account
  and by :envvar:`pki_private_group` – this can be used to limit access to
  different private keys by different UNIX accounts.

:file:`default.pem`
  This file contains the private key, server certificate and Intermediate
  CA certificate(s). It has the same restrictions as the private key – can be
  read only by the ``root`` account and by :envvar:`pki_private_group`.

:file:`trusted.crt`
  This is the complete trust chain of intermediate and root CA certificates,
  without the server certificate, similar to :file:`CA.crt`. It is used for
  automatic OCSP stapling verification by the server, and works with the
  primary CA in case the alternative Certificate Authority is used for client
  certificates.

All of the above filenames are static, which means that the only thing you need
to change to select a different PKI realm is the realm directory name.

Example nginx configuration
---------------------------

To use the ``domain`` realm in your :program:`nginx` configuration, you can add
something similar to this example in your configuration file:

.. code-block:: nginx

   server {
       listen [::]:443 ssl;

       # HTTPS support
       ssl_certificate         /etc/pki/realms/domain/default.crt;
       ssl_certificate_key     /etc/pki/realms/domain/default.key;

       # OCSP Stapling support
       ssl_stapling            on;
       ssl_stapling_verify     on;
       ssl_trusted_certificate /etc/pki/realms/domain/trusted.crt;

       # X.509 Client certificate support
       ssl_verify_client       optional;
       ssl_verify_depth        2;
       ssl_trusted_certificate /etc/pki/realms/domain/CA.crt;
   }

This configuration explains where each certificate is used, but this is not
sufficient to enable HTTPS for the webserver. Refer to the :program:`nginx`
documentation for the rest of the required configuration options.

If you use the ``debops.nginx`` Ansible role provided with the project, it has
extensive integration with the ``debops.pki`` role and can configure the
webserver automatically. Usually all you need to do is to make sure the default
realm matches the one you would like to use for each server configuration.

The PKI realm directory structure
---------------------------------

This is an example ``domain`` realm directory, created on each remote host
managed by ``debops.pki``. The current set of certificates active in this realm
is provided by the internal ``debops.pki`` Certificate Authority:

.. code-block:: none

   /etc/pki/realms/
   └── domain/
       ├── acme/
       ├── config/
       │   └── realm.conf
       ├── external/
       ├── internal/
       │   ├── alt_intermediate.pem
       │   ├── alt_root.pem
       │   ├── cert.pem
       │   ├── gnutls.conf
       │   ├── intermediate.pem
       │   ├── request.pem
       │   └── root.pem
       ├── private/
       │   ├── key_chain_dhparam.pem
       │   ├── key_chain.pem
       │   ├── key.pem
       │   └── realm_key.pem
       ├── public/
       │   ├── alt_intermediate.pem -> ../internal/alt_intermediate.pem
       │   ├── alt_intermediate_root.pem
       │   ├── alt_root.pem -> ../internal/alt_root.pem
       │   ├── alt_trusted.pem -> alt_intermediate_root.pem
       │   ├── cert_intermediate_dhparam.pem
       │   ├── cert_intermediate.pem
       │   ├── cert.pem -> ../internal/cert.pem
       │   ├── cert.pem.sig
       │   ├── chain.pem -> cert_intermediate_dhparam.pem
       │   ├── full.pem
       │   ├── intermediate_root.pem
       │   ├── root.pem -> ../internal/root.pem
       │   └── trusted.pem -> intermediate_root.pem
       ├── selfsigned/ (optional)
       │   ├── cert.pem
       │   ├── gnutls.conf
       │   ├── request.pem
       │   └── root.pem -> cert.pem
       ├── CA.crt -> public/alt_trusted.pem
       ├── default.crt -> public/chain.pem
       ├── default.key -> private/key.pem
       ├── default.pem -> private/key_chain_dhparam.pem
       └── trusted.crt -> public/trusted.pem

On the Ansible Controller, there's a corresponding directory structure located
in the :file:`secret/` directory maintained by the :ref:`debops.secret` Ansible role:

.. code-block:: none

    secret/pki/
    ├── realms/
    │   ├── by-group/
    │   │   └── all/
    │   │       └── domain/
    │   │           ├── external/
    │   │           └── private/
    │   └── by-host/
    │       └── hostname.example.com/
    │           └── domain/
    │               ├── external/
    │               ├── internal/
    │               │   ├── alt_intermediate.pem
    │               │   ├── alt_root.pem
    │               │   ├── cert.pem
    │               │   ├── intermediate.pem
    │               │   └── root.pem
    │               └── private/
    └── requests/
        └── domain/
            └── hostname.example.com/
                └── domain/
                    └── request.pem

Your version might not contain all of the shown files and symlinks, for example
the :file:`alt_*.pem` versions of intermediate and root CA certificates are only
present if an alternative CA is configured.

Both directories are maintained and kept in sync using two Bash scripts
provided by the role, :program:`pki-realm` and :program:`pki-authority`. Ansible tasks are
used to copy files to and from Ansible Controller to remote hosts.

How a PKI realm is created
--------------------------

Each PKI realm starts with a simple directory structure created on the Ansible
Controller in the :file:`secret/` directory:

.. code-block:: none

    secret/pki/
    └── realms/
        ├── by-group/
        │   └── all/
        │       └── domain/
        │           ├── external/
        │           └── private/
        └── by-host/
            └── hostname.example.com/
                └── domain/
                    ├── external/
                    ├── internal/
                    └── private/

These directories are created at the beginning, so that Ansible can copy
private files before the actual PKI realm creation on remote hosts. This can be
used to provide a set of identical private RSA keys to multiple hosts at once
(using the directories in :file:`private/` subdirectories) or custom scripts that
access external Certificate Authorities (using :file:`external/` subdirectories).

Next, PKI realm directories are created on the remote host:

.. code-block:: none

    /etc/pki/realms/
    └── domain/
        ├── acme/
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        ├── private/
        └── public/

The :file:`config/realm.conf` file contains a set of Bash variables that define
different parameters of the PKI realm, for example the default DNS domain used
to generate the certificates, owner and group of various directories and files,
permissions applied to various directory and file types, and so on.

The :file:`acme/`, :file:`external/` and :file:`internal/` subdirectories hold
data files for different Certificate Authorities. Each CA is described in more
detail in a separate document, here is a brief overview:

:file:`acme/`
  This directory is for certificates issued using ACME_ (for example `Let's Encrypt`_).
  It will be activated and used automatically when a host has a public IP address
  and the :program:`nginx` webserver is installed and configured to support ACME
  Challenges (see the debops.nginx_ role for more details).

:file:`external/`
  This directory is used to manage certificates signed by an external
  Certificate Authority. To do this, you need to provide a special :file:`script`
  file, which will be executed with a set of environment variables. This can be
  used to request a certificate from an external CA, like Active Directory or
  FreeIPA, or download a certificate from an external location.

  An alternative is to provide an already signed :file:`cert.pem` file and
  optionally the :file:`intermediate.pem` and :file:`root.pem` files.

:file:`internal/`
  This directory is used by the internal ``debops.pki`` Certificate Authority
  to transfer certificate requests as well as certificates.

If the internal CA is disabled either globally for a host, or for a particular
PKI realm, an alternative directory, :file:`selfsigned/` will be created. It
will hold a self-signed certificate, not trusted by anything else (not even the
host that has created it). This is done, so that services depending on the
existence of the private keys and certificates can function correctly at all
times.

The :program:`pki-realm` script, located in :file:`/usr/local/lib/pki` on
remote hosts, checks which of these directories have valid
certificates in order of :envvar:`pki_authority_preference`, and the first
valid one is used as the "active" directory.  Files from the active directory
are symlinked to the :file:`public/` directory.

The :file:`public/` directory holds the currently active certificates which are
symlinks to the real certificate files in one of the active directories mentioned above.
Some additional files are also created here by the :program:`pki-realm` script, namely
the certificate chain (server certificate + intermediate certificates) and the
trusted chain (intermediate certificates + root certificate). The full
certificate contains server certificate + intermediate certificates + root
certificate, which might be required by some applications.

The :file:`private/` directory holds the private key of a given realm. Access to
this directory and files inside is restricted by UNIX permissions and only
a specific system group (usually ``ssl-cert``, but it can be configured) is
allowed to access the files inside.

The next step is the creation of all necessary files, like private/public keys,
certificate requests, etc. At this point, if Ansible was provided with a
private RSA key to use, it will copy it to the :file:`private/` directory.
After that, all necessary files are created by the :program:`pki-realm` script
on the remote host. The directory structure changes a bit:

.. code-block:: none

    /etc/pki/realms/
    └── domain/
        ├── acme/
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        │   ├── gnutls.conf
        │   └── request.pem
        ├── private/
        │   ├── key.pem
        │   └── realm_key.pem
        ├── public/
        ├── CA.crt -> /etc/ssl/certs/ca-certificates.crt
        └── default.key -> private/key.pem

As you can see, the configuration of a Certificate Request for an internal CA
has been created, and the :file:`internal/request.pem` file has been generated,
using the :file:`private/key.pem` RSA key. By default, if no :file:`root.pem`
certificate is provided, the system CA certificate store is symlinked as
:file:`CA.crt`.

Afterwards, Ansible uploads the generated `Certificate Signing Request`_ (CSR_) to
the Ansible Controller for the internal CA to sign (if it's enabled). The CSR is
uploaded to the :file:`secret/` directory:

.. code-block:: none

    secret/pki/
    ├── realms/
    │   ├── by-group/
    │   │   └── all/
    │   │       └── domain/
    │   │           ├── external/
    │   │           └── private/
    │   └── by-host/
    │       └── hostname.example.com/
    │           └── domain/
    │               ├── external/
    │               ├── internal/
    │               └── private/
    └── requests/
        └── domain/
            └── hostname.example.com/
                └── domain/
                    └── request.pem

To avoid possible confusion, the :file:`secret/pki/requests/domain/` directory
points to the "domain" internal CA which is an intermediate CA located under
the "root" CA. The :file:`hostname.example.com/domain/` directory inside the
:file:`domain/` directory points to the "domain" realm on the
``hostname.example.com`` host.

When all of the requests from the remote hosts are uploaded to the Ansible
Controller, the :program:`pki-authority` script inside the :file:`secret/lib` directory takes
over and performs certificate signing for all of the currently managed hosts.
The certificate named :file:`cert.pem` is placed in the :file:`internal/`
directory of each host according to the realm the request came from.

In addition to the certificates, the CA intermediate and root certificates are
also symlinked to the :file:`internal/` directory, so that Ansible can
automatically copy their contents to the remote hosts. If a particular
Certificate Authority indicates that an alternative CA should be present, the
``alt_*.pem`` versions of intermediate and root certificates are also symlinked
there:

.. code-block:: none

    secret/pki/
    ├── realms/
    │   ├── by-group/
    │   │   └── all/
    │   │       └── domain/
    │   │           ├── external/
    │   │           └── private/
    │   └── by-host/
    │       └── hostname.example.com/
    │           └── domain/
    │               ├── external/
    │               ├── internal/
    │               │   ├── alt_intermediate.pem
    │               │   ├── alt_root.pem
    │               │   ├── cert.pem
    │               │   ├── intermediate.pem
    │               │   └── root.pem
    │               └── private/
    └── requests/
        └── domain/
            └── hostname.example.com/
                └── domain/
                    └── request.pem

When all of the requests have been processed, Ansible copies the content of the
directories to remote hosts. The content of the :file:`by-host/` directory is copied
first and overwrites all files that are present on remote hosts, the
:file:`by-group/` directory content is copied only when the corresponding files
are not present. This allows the administrator to provide the shared scripts or
private keys/certificates as needed, per host, per group or for all managed
hosts.

After certificates signed by the internal CA are downloaded to remote hosts,
the directory structure might look similar to:

.. code-block:: none

    /etc/pki/realms/
    └── domain/
        ├── acme/
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        │   ├── alt_intermediate.pem
        │   ├── alt_root.pem
        │   ├── cert.pem
        │   ├── gnutls.conf
        │   ├── intermediate.pem
        │   ├── request.pem
        │   └── root.pem
        ├── private/
        │   ├── key.pem
        │   └── realm_key.pem
        ├── public/
        ├── CA.crt -> /etc/ssl/certs/ca-certificates.crt
        └── default.key -> private/key.pem

Other authority directories (:file:`acme/` and :file:`external/`) might also
contain various files.

After certificates are copied from the Ansible Controller, the
:program:`pki-realm` script is executed again for each PKI realm configured on
a given host. It checks which authority directories have valid
certificates, picks the first viable one according to
:envvar:`pki_authority_preference` and activates them.

Certificate activation entails symlinking the certificate, intermediate and
root files to the :file:`public/` directory and generation of various chain files:
certificate + intermediate, intermediate + root and key + certificate
+ intermediate (which is stored securely in the :file:`private/` directory).

Some applications do not support a separate :file:`dhparam` file, and instead expect
that the DHE parameters are present after the X.509 certificate chain. If the
debops.dhparam_ role has been configured on a host and Diffie-Hellman
parameter support is enabled in a given PKI realm, DHE parameters will be
appended to the final certificate chains (both public and private). When
debops.dhparam_ regenerates the parameters, the :program:`pki-realm` script will
automatically detect the new ones and update the certificate chains.

The end result is a fully configured PKI realm with a set of valid certificates
available for other applications and services:

.. code-block:: none

    /etc/pki/realms/
    └── domain/
        ├── acme/
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        │   ├── alt_intermediate.pem
        │   ├── alt_root.pem
        │   ├── cert.pem
        │   ├── gnutls.conf
        │   ├── intermediate.pem
        │   ├── request.pem
        │   └── root.pem
        ├── private/
        │   ├── key_chain_dhparam.pem
        │   ├── key_chain.pem
        │   ├── key.pem
        │   └── realm_key.pem
        ├── public/
        │   ├── alt_intermediate.pem -> ../internal/alt_intermediate.pem
        │   ├── alt_intermediate_root.pem
        │   ├── alt_root.pem -> ../internal/alt_root.pem
        │   ├── alt_trusted.pem -> alt_intermediate_root.pem
        │   ├── cert_intermediate_dhparam.pem
        │   ├── cert_intermediate.pem
        │   ├── cert.pem -> ../internal/cert.pem
        │   ├── cert.pem.sig
        │   ├── chain.pem -> cert_intermediate_dhparam.pem
        │   ├── full.pem
        │   ├── intermediate_root.pem
        │   ├── root.pem -> ../internal/root.pem
        │   └── trusted.pem -> intermediate_root.pem
        ├── CA.crt -> public/alt_trusted.pem
        ├── default.crt -> public/chain.pem
        ├── default.key -> private/key.pem
        ├── default.pem -> private/key_chain_dhparam.pem
        └── trusted.crt -> public/trusted.pem

During this process, at various stages special "hook" scripts might be run,
which can react to events like realm creation, activation of new certificates
and so on.
