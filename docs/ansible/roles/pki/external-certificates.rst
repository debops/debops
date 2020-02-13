.. _external_certificates:

External certificates
=====================

The PKI realms managed by the ``debops.pki`` role support management of private
keys and certificates from external Certificate Authorities. You can either
provide a set of valid certificates with corresponding private keys,
or use a script with a custom environment to request a certificate remotely from
an external Certificate Authority.

Required files
--------------

For the :program:`pki-realm` script to correctly recognize and enable external
certificates, you need to provide a set of specific files, either statically
through the :file:`secret/` directory or by creating them using a script (see
below). All paths are relative to the main PKI realm directory, for example
:file:`/etc/pki/realms/example.com/`:

:file:`private/key.pem`
  Private key used by a specific PKI realm. If not present, the :program:`pki-realm`
  script will generate one automatically before executing the external script.

:file:`external/cert.pem`
  Required. The certificate signed by an external Certificate Authority, in PEM
  format.

:file:`external/intermediate.pem`
  Set of intermediate CA certificates which signed the realm certificate. They
  will be chained together with the realm certificate automatically.

:file:`external/root.pem`
  The certificate of the Root Certificate Authority. It will be chained with
  the intermediate CA certificates for OCSP stapling purposes.

:file:`external/script`
  A custom script (any language should work, however you need to take care of
  additional dependencies) which will be executed on the remote host if found,
  with a set of environment variables. The script will be executed inside the
  :file:`external/` directory of a given realm.

Static private keys and certificates
------------------------------------

When the ``debops.pki`` Ansible role is run, it creates a set of directories on
the Ansible Controller in the :file:`secret/` directory:

.. code-block:: none

    secret/pki/
    └── realms/
        ├── by-group/
        │   ├── all/
        │   │   └── domain/
        │   │       ├── external/
        │   │       └── private/
        │   └── inventory_group/
        │       └── domain/
        │           ├── external/
        │           └── private/
        └── by-host/
            └── hostname.example.com/
                └── domain/
                    ├── external/
                    ├── internal/
                    └── private/

As you can see, the directory structure reflects the Ansible inventory model:

- :file:`realms/by-group/all/` -> :file:`inventory/group_vars/all/`
- :file:`realms/by-group/inventory_group/` -> :file:`inventory/group_vars/inventory_group/`
- :file:`realms/by-host/hostname.example.com/` -> :file:`inventory/host_vars/hostname.example.com/`

Each of those directories has a set of subdirectories for configured PKI
realms, with the :file:`external/`, :file:`internal/` and :file:`private/` directories
corresponding to the same ones on the remote hosts. Ansible at different stages
of the ``debops.pki`` role run will copy contents of these directories to
remote hosts, in a specific order:

- contents of the :file:`realms/by-host/<hostname>` directories for each host
  will be copied and overwrite already present files;
- contents of the :file:`realms/by-group/<group_name>/` directories will be
  copied next, but will not overwrite already existing files. Only hosts that
  are in a given inventory group will receive the corresponding files;
- and finally, contents of the :file:`realms/by-group/all/` directory will be
  copied to all currently managed remote hosts, but won't overwrite already
  present files;

You can use this to distribute already issued certificates with their private
keys. Putting them in :file:`realms/by-group/all/` directory will ensure that all
hosts will have the same set of keys and certificates. If you put them in
a specific group directory, only hosts in that group will receive the files.
Files put in a specific host directory will only be copied to that host.

The private keys will be copied to remote hosts before the PKI realm is
created, which means that any potential ACME or internal certificates will use
them instead of automatically generated ones. This might be useful if you need
to have several hosts which use the same set of private keys.

The above mechanism is used to distribute certificates from internal
Certificate Authorities, using the :file:`internal/` directory.

Because files copied from :file:`by-group/all/` and :file:`by-group/inventory_group/`
directories are not overwritten automatically, you will need to remove the
corresponding files on remote hosts yourself if you want to update them.

The :envvar:`pki_inventory_groups` default variable is a list of Ansible inventory
groups that will have their corresponding directories. You need to specify your
custom inventory groups in order to have them "active".

Certificates managed by a custom script
---------------------------------------

You can create a custom script and store it in above directories as
:file:`external/script` (permissions are not important). It will be copied to
the remote host, made executable and run by the :program:`pki-realm` script with the
:file:`external/` directory as the current working directory. You can use this
to provide additional files needed by the Certificate Authority. The expected
output of the script is a set of files mentioned above.

The script will be executed under the ``root`` account, with a set of
``$PKI_SCRIPT_*`` environment variables:

``$PKI_SCRIPT_REALM``
  Contains the name of the current PKI realm, set in ``item.name`` parameter.

``$PKI_SCRIPT_FQDN``
  Contains Fully Qualified Domain Name used as the default domain if the realm
  does not specify one in it's name.

``$PKI_SCRIPT_SUBJECT``
  Contains the Distinguished Name, or subject of the certificate, each element
  separated by the ``/`` character, similar to the format of the :command:`openssl req
  -subj` option.

``$PKI_SCRIPT_DOMAINS``
  List of apex (root) domains configured for the realm, separated by the ``/``
  character.

``$PKI_SCRIPT_SUBDOMAINS``
  List of subdomains which should be added to each apex domain, each one
  separated by the ``/`` character. The special ``_wildcard_`` name means
  a wildcard subdomain (``*.example.com``).

``$PKI_SCRIPT_PRIVATE_KEY``
  Absolute path to the private key of the current PKI realm.

``$PKI_SCRIPT_DEFAULT_CRT``
  Absolute path to the current PKI realm certificate chain, expected to be used
  in the application configuration files.

``$PKI_SCRIPT_DEFAULT_KEY``
  Absolute path to the current PKI realm private key, expected to be used in
  the application configuration files.

``$PKI_SCRIPT_DEFAULT_PEM``
  Absolute path to the current PKI realm combined private key and certificate
  chain, expected to be used in the application configuration files.

``$PKI_SCRIPT_STATE``
  A list of PKI realm states separated by the ``,`` character. You can inspect
  this variable to determine the current state of the current realm
  (initialization, activation of new certificates, changed files) and react to
  it in the script.

Because the operation of the PKI realm is stateless, the external script will be
executed multiple times during ``debops.pki`` run. The state in which the realm
is in will be present in the ``$PKI_SCRIPT_STATE`` variable and using that you can
perform various operations, like issuing a new certificate request when the
realm is created.
