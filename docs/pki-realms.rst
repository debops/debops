.. _pki_realms_structure:

PKI realms structure
====================

The concept of PKI realms is designed to provide a standardized way for various
applications to access X.509 certificates and private keys. The management of
the keys and certificates is moved outside of the application into a fixed
directory and file structure, which other applications can access.

.. contents::
   :local:

The application view
--------------------

Different applications have different requirements for X.509 certificates and
private keys. Some of them support keys and certificates in separate files,
others require them combined in a single file. The PKI realm is designed to
support both schemes at once.

The realms are located in ``/etc/pki/realms/`` directory. Each realm is
contained in its own subdirectory. By default a ``domain`` realm is configured
by the role, and its simplified directory structure looks like this::

    /etc/pki/realms/
    └── domain/
        ├── CA.crt
        ├── default.crt
        ├── default.key
        ├── default.pem
        └── trusted.crt

Each of these files is a symlink to a subdirectory (see the next section). The
contents of these files are:

``CA.crt``
  This is the "trust anchor", or Root Certificate Authority certificate used by
  the application to check the validity of client certificates. This file is
  publicly readable.

  This file may contain a CA certificate different than the one that issued the
  server certificate. In this case, this can be used to have separate client
  and server Certificate Authorities.

``default.crt``
  This is the server certificate with optional bundle of Intermediate
  Certificate Authorities. It is sent to the clients by the application. This
  file is publicly readable.

``default.key``
  This is the server private key. It's readable only by the ``root`` account
  and by selected UNIX group - this can be used to limit access to different
  private keys by different UNIX accounts.

``default.pem``
  This file contains combined private key and server certificate + Intermediate
  CA bundle. It has the same restrictions as the private key - can be read only
  by ``root`` account and selected UNIX group.

``trusted.crt``
  This is the complete trust chain of intermediate and root CA certificates,
  without the server certificate, similar to ``CA.crt``. It is used for
  automatic OCSP stapling verification by the server, and works with the
  primary CA in case the alternative Certificate Authority is used for client
  certificates.

All of the above filenames are static, which means that only thing you need to
change to select a different PKI realm is the realm directory name.

Example nginx configuration
---------------------------

To use the ``domain`` realm in your ``nginx`` configuration, you can add
something similar to this example in your config file:

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
sufficient configuration to enable HTTPS webserver. Refer to the ``nginx``
documentation for the rest of the required configuration options.

If you use the ``debops.nginx`` Ansible role provided with the project, it has
extensive integration with the ``debops.pki`` role and can configure the
webserver automatically. Usually all you would need to do is to specify
a default realm for each server configuration, if the incorrect one is
detected.

The PKI realm directory structure
---------------------------------

This is an example ``domain`` realm directory, created on each remote host
managed by ``debops.pki``. The current set of certificates active in this realm
is provided by the internal ``debops.pki`` Certificate Authority::

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
        │   ├── intermediate_root.pem
        │   ├── root.pem -> ../internal/root.pem
        │   └── trusted.pem -> intermediate_root.pem
        ├── CA.crt -> public/alt_trusted.pem
        ├── default.crt -> public/chain.pem
        ├── default.key -> private/key.pem
        ├── default.pem -> private/key_chain_dhparam.pem
        └── trusted.crt -> public/trusted.pem

On the Ansible Controller, there's a corresponding directory structure located
in the ``secret/`` directory maintained by the ``debops.secret`` Ansible role::

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
the ``alt_*.pem`` versions of intermediate and root CA certificates are only
present if an alternative CA is configured.

Both directories are maintained and kept in sync using two Bash scripts
provided by the role, ``pki-realm`` and ``pki-authority``. Ansible tasks are
used to copy files to and from Ansible Controller to remote hosts.

How a PKI realm is created
--------------------------

Each PKI realm starts with a simple directory structure created on the Ansible
Controller in the ``secret/`` directory::

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
(using the directories in ``private/`` subdirectories) or custom scripts that
access external Certificate Authorities (using ``external/`` subdirectories).

Next, PKI realm directories are created on the remote host::

    /etc/pki/realms/
    └── domain/
        ├── acme/
        ├── config/
        │   └── realm.conf
        ├── external/
        ├── internal/
        ├── private/
        └── public/

The ``config/realm.conf`` file contains a set of Bash variables that define
different parameters of the PKI realm, for example the default DNS domain used
to generate the certificates, owner and group of various directories and files,
permissions applied to various directory and file types, and so on.

The ``acme/``, ``external/`` and ``internal/`` subdirectories hold data files
for different Certificate Authorities. Each CA is described in more detail in
a separate document, here is a brief overview:

``acme/``
  This is directory used by the ACME Certificate Authority (currently only the
  `Let's Encrypt <https://www.letsencrypt.org/>`_ CA supports this protocol).
  It will be activated and used automatically when a host has a public IP address
  and the ``nginx`` webserver is installed and configured to support ACME
  Challenges (see the ``debops.nginx`` role for more details).

``external/``
  This directory is used to manage certificates signed by an external
  Certificate Authority. To do this, you need to provide a special ``script``
  file, which will be executed with a set of environment variables. This can be
  used to request a certificate in and external CA, like Active Directory or
  FreeIPA, or download a signed certificate from external location.

  An alternative is to provide already signed ``cert.pem`` file with optional
  ``intermediate.pem`` and ``root.pem`` certificates.

``internal/``
  This directory is used by the internal ``debops.pki`` Certificate Authority
  to transfer certificate requests as well as signed certificates.

The ``pki-realm`` script checks which of these directories have signed and
valid certificates in order (``external``, ``acme``, ``internal``), and the
first valid one is used as the "active" directory. Files from the active
directory are symlinked to the ``public/`` directory.

The ``public/`` directory holds currently active certificates which are
symlinks to the real certificate files in one of the active directories above.
Some additional files are also created here by the ``pki-realm`` script, namely
the certificate chain (server certificate + intermediate certificates) and the
trusted chain (intermediate certificates + root certificate).

The ``private/`` directory holds the private key of a given realm. Access to
this directory and files inside is restricted by UNIX permissions and only
a specific system group (usually ``ssl-cert``, but it can be configured) is
allowed to access the files inside.

The next step is the creation of all necessary files, like private/public keys,
certificate requests, etc. At this point, if Ansible was provided with a
private RSA key to use, it will copy it to the ``private/`` directory. After
that, all necessary files are created by the ``pki-realm`` script on remote
host. The directory structure changes a bit::

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
has been created, and the ``internal/request.pem`` file has been generated,
using the ``private/key.pem`` RSA key. By default, if no ``root.pem``
certificate is provided, the system CA certificate store is symlinked as
``CA.crt``.

Afterwards, Ansible uploads the generated Certificate Signing Request to the
Ansible Controller for the internal CA to sign (if it's enabled). CSR is
uploaded to the ``secret/`` directory::

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

To avoid possible confusion, the ``secret/pki/requests/domain/`` directory
points to the "domain" internal CA which is an intermediate CA located under
"root" CA. The ``hostname.example.com/domain/`` directory inside the
``domain/`` directory points to the "domain" realm on the
``hostname.example.com`` host.

When all of the requests from the remote hosts are uploaded to the Ansible
Controller, the ``pki-authority`` script inside the ``secret/`` directory takes
over and performs certificate signing for all of the currently managed hosts.
The signed certificate named ``cert.pem`` is placed in the ``internal/``
directory of each host according to the realm the request came from.

In addition to the certificates, the CA intermediate and root certificates are
also symlinked to the ``internal/`` directory, so that Ansible can
automatically copy their contents to the remote hosts. If a particular
Certificate Authority indicates that an alternative CA should be present, the
``alt_*.pem`` versions of intermediate and root certificates are also symlinked
there::

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

When all of the requests have been processed, Ansible copies contents of the
directories to remote hosts. The ``by-host/`` directory contents are copied
first and overwrite any files that are present on remote hosts, the
``by-group/`` directory contents are copied only when the corresponding files
are not present. This allows the administrator to provide the shared scripts or
private keys/certificates as needed, per host, per group or for all managed
hosts.

After certificates signed by internal CA are downloaded to remote host, the
directory structure might look similar to::

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

Other authority directories (``acme/`` and ``external/``) might also contain
various files.

After certificates are copied from Ansible Controller, ``pki-realm`` script is
executed again for each PKI realm configured on a given host. It checks which
authority directories have signed and valid certificates, picks the first
viable one according to the preference (``external``, ``acme``, ``internal``),
and activates them.

Certificate activation entails symlinking the certificate, intermediate and
root files to the ``public/`` directory and generation of various chain files
- certificate + intermediate, intermediate + root and key + certificate
+ intermediate (which is stored securely in the ``private/`` directory).

Some applications do not support separate ``dhparam`` file, and instead expect
that the DHE parameters are present after the X.509 certificate chain. If the
``debops.dhparam`` role has been configured on a host and Diffie-Hellman
parameter support is enabled in a given PKI realm, DHE parameters will be
appended to the final certificate chains (both public and private). When the
``debops.dhparam`` regenerates the parameters, ``pki-realm`` script will
automatically detect the new ones and update the certificate chains.

The end result is fully configured PKI realm with a set of valid certificates
available for other applications and services::

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

