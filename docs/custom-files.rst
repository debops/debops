.. _custom_file_management:

Custom file management
======================

If you need to, you can copy custom files or even create files with content in
YAML templates using a set of list variables. You can use this feature to for
example install private keys and certificates stored as YAML text blocks in
a file encrypted with ``ansible-vault`` which is unlocked during Ansible run.

Each element of the file list is a dict with specific parameters:

``src``
  Required, unless ``content`` is specified. Path to a file on the Ansible
  Controller, which will be copied to remote host.

``content``
  Required, unless ``src`` is specified. A YAML text block or a Jinja variable,
  contents of which will be copied to specified file on remote host.

``dest``
  Required. Path to the destination file on remote host.

``owner``
  Owner of the created file, by default ``root``.

``group``
  File group, depending on the file type it will be ``root`` (for public files)
  or a group specified by the ``pki_private_group`` variable, usually
  ``ssl-cert`` (for private files).

``mode``
  File permissions, by default public files are copied with permissions ``644``
  and private files will have ``640`` permissions.

``force``
  Boolean. If ``True`` (default), an existing file will be replaced with the
  specified file or contents.

There are multiple list variables which can be used on multiple inventory
levels:

- all hosts in the inventory:
  - ``pki_private_files``
  - ``pki_public_files``
- hosts in specific inventory group:
  - ``pki_group_private_files``
  - ``pki_group_public_files``
- specific hosts:
  - ``pki_host_private_files``
  - ``pki_host_public_files``

The private files will be copied before PKI realms are created, so that you can
provide private keys if you want to. Public files will be copied after PKI
realms are created, and internal certificates are signed.

Examples
~~~~~~~~

Instal custom private key from a Jinja variable on all hosts:

.. code-block:: yaml

   pki_private_files:
     - content: '{{ custom_variable }}'
       dest: '/etc/pki/realms/domain/private/key.pem'

