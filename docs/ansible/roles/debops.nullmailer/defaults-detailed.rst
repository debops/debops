Default variable details
========================

Some of ``debops.nullmailer`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _nullmailer__ref_remotes:

nullmailer__remotes
-------------------

This list, as well as :envvar:`nullmailer__default_remotes`, is used to configure
where ``nullmailer`` should forward all mail messages. Each element of a list
can be either a string that defines the exact line in the
:file:`/etc/nullmailer/remotes` configuration file, or a YAML dictionary with
following parameters:

``host``
  Required. DNS hostname of the SMTP server to which all messages will be
  forwarded.

``protocol``
  Optional. Specify the daemon from :file:`/usr/lib/nullmailer/` which should be
  used to send the mail messages. Either ``smtp`` (default) or ``qmtp``.

``port``
  Optional. Specify the port to connect. If not specified, ``25`` will be used
  as default.

``starttls``
  Optional, boolean. If not specified and :envvar:`nullmailer__starttls` is enabled,
  each configured SMTP server will be asked to provide encrypted connection
  using ``STARTTLS`` command. If ``item.ssl`` or ``item.options`` parameters
  are specified, the ``STARTTLS`` support is not enabled by default.

``ssl``
  Optional, boolean. If enabled, new connections to this SMTP server will
  automatically be encrypted using SSL. This usually requires a different port
  for communication, typically ``465``.

``insecure``
  Optional, boolean. By default when encrypted connections are used,
  ``nullmailer`` checks the validity of the X.509 certificate provided by the
  server. If this parameter is enabled, the validity checks won't be performed.

``x509cafile``
  Optional. Specify absolute path to the X.509 Certificate Authority
  certificate which should be used to validate the certificate of a given SMTP
  server. If not specified, the system-wide CA database will be used.

``x509certfile``
  Optional. Specify absolute path to the X.509 certificate which should be
  presented to the remote SMTP server for authentication.

``x509crlfile``
  Optional. Specify absolute path to the CRL file which should be used to
  validate the certificate provided by the remote SMTP server.

``x509fmtder``
  Optional, boolean. If enabled, indicates that the specified certificates are
  in DER format (PEM otherwise).

``auth`` or ``auth_login``
  Optional, boolean. If enabled, indicates that the specified sever requires
  user authentication before accepting forwarded mail messages.

``user``
  Optional. Specify the username which should be used to login to the remote
  SMTP server.

``pass`` or ``password``
  Optional. Specify the password which should be used to login to the remote
  SMTP server.

``options``
  Optional. Custom list of options recognized by the ``nullmailer`` protocol
  modules. Check the usage information in the :file:`/usr/lib/nullmailer/*`
  commands to see possible options, and examples below to see how they can be
  used.

Examples
~~~~~~~~

Configure a remote SMTP server without TLS encryption:

.. code-block:: yaml

   nullmailer__remotes:
     - host: 'mx.example.org'
       starttls: False

Configure a remote SMTP server with mail messages delivered via ``submission``
protocol:

.. code-block:: yaml

   nullmailer__remotes:
     - host: 'mail.example.org'
       port: '587'
       auth: True
       user: 'username'
       pass: 'password'

Configure GMail as remote SMTP server with options specified manually:

.. code-block:: yaml

   nullmailer__remotes:
     - host: 'smtp.gmail.com'
       options: [ '--starttls', '--port=587', '--auth-login',
                  '--user=username', '--pass=password' ]


.. _nullmailer__ref_configuration_files:

nullmailer__configuration_files
-------------------------------

This list, as well as :envvar:`nullmailer__private_configuration_files`,
manages configuration files used by the ``nullmailer`` service. Each entry in
the list is a YAML dictionary with parameters:

``dest``
  Required. Absolute path to the configuration file.

``content``
  File contents which should be placed in the configuration file. If it results
  in an empty string, file will be empty. Not needed if ``item.src`` is
  specified.

``src``
  Absolute path to the source file located on the Ansible Controller.
  Not needed if ``item.content`` is specified.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  created. If ``absent``, the configuration file will be removed.

``purge``
  Optional, boolean. If not specified, file will be added to the list of files
  to be purged when the ``nullmailer`` package is purged. If set and ``False``,
  file will not be purged with other files.

  See :ref:`nullmailer__ref_purge_files` for more details.

``owner``
  Optional. Specify an user account which should be the owner of the
  configuration file. The user account must already exist.

``group``
  Optional. Specify what group the configuration file belongs to. The group
  must already exist.

``mode``
  Optional. Specify the file attributes which should be set for the
  configuration file.

You can find the usage examples of these lists in the role
:file:`defaults/main.yml` file.


.. _nullmailer__ref_purge_files:

nullmailer__purge_files
-----------------------

The ``debops.nullmailer`` role supports easy switch to a different SMTP server
by creating a :command:`dpkg` hook script that removes the additional files and custom
services configured by the role when the ``nullmailer`` package is removed or
purged.  This ensures that the new SMTP server can be correctly installed by
the package manager without the need for the ``debops.nullmailer`` role to be
involved in the process.

The :envvar:`nullmailer__purge_files` and :envvar:`nullmailer__purge_default_files` lists
specify which files should be purged by the hook script. In addition, all
configuration files mentioned in :envvar:`nullmailer__configuration_files` and
:envvar:`nullmailer__private_configuration_files` will be purged as well, unless the
``item.purge`` parameter is present and set to ``False``.
