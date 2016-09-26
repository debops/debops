.. _system_ca_certificates:

System CA certificates
======================

On Debian GNU/Linux and it's derivative distributions, management of Root
Certificate Authority certificates is performed by the ``ca-certificates``
package. This package maintains a list of active Root CA certificates in the
:file:`/etc/ca-certificates.conf` configuration file, and stores the certificates
themselves in the :file:`/etc/ssl/certs/` directory.

The ``debops.pki`` role has several variables which can be used to control what
Root Certificate Authorities are trusted by the system, as well as supports
easy installation of local or custom Root Certificate Authorities.

Configuration of system CA certificates
---------------------------------------

The :file:`/etc/ca-certificates.conf` configuration file specifies which
certificates will be trusted by the system. This is done by specifying names of
certificate files located in the :file:`/usr/share/ca-certificates/` directory.
The specified certificate files will be included in the system CA store. If a
given filename is prefixed with ``!``, a given certificate will be excluded
from the system CA store.

By default, Debian hosts automatically trust new Root Certificate Authorities
added in the ``ca-certificates`` package. To control this, you can use
:envvar:`pki_system_ca_certificates_trust_new` boolean variable. Setting this
variable to ``True`` will ensure that new Root CA certificates are trusted.
Setting it to ``False`` will not enable new CA certificates automatically.

You can use :envvar:`pki_system_ca_certificates_blacklist` and
:envvar:`pki_system_ca_certificates_whitelist` list variables to define which
certificates will be excluded/included in the CA store. Each list element is
a regexp of the certificate file name. If a given file is found in both lists,
it will be excluded from the certificate store.

To find out the names of the certificate files you can use, check the contents
of the :file:`/etc/ca-certificates.conf` configuration file.

Examples
~~~~~~~~

Blacklist all certificates:

.. code-block:: yaml

   pki_system_ca_certificates_blacklist:
     - '.*'

Blacklist all certificates provided in the Mozilla CA list:

.. code-block:: yaml

   pki_system_ca_certificates_blacklist:
     - 'mozilla/.*'

Blacklist all VeriSign certificates:

.. code-block:: yaml

   pki_system_ca_certificates_blacklist:
     - '.*VeriSign.*'

Local Root CA certificates
--------------------------

Contents of the :file:`secret/pki/ca-certificates/` directory located on the
Ansible Controller will be copied to all of the remote hosts by the
``debops.pki`` role, to the :file:`/usr/local/share/ca-certificates/pki/`
directory. After that, they will be automatically added to the system Root CA
store using the :command:`update-ca-certificates` script.

Note that already present CA certificates on remote hosts with the same name
are not updated after the first download unless the CA certificates are by
host.

The internal Root Certificate Authorities created by the ``debops.pki`` role
will have their certificates automatically symlinked in the
:file:`secret/pki/ca-certificates/` directory. You can prevent that by adding an
``item.system_ca: False`` parameter in the CA configuration variable.
