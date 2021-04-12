.. Copyright (C) 2016-2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2016-2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of ``debops.authorized_keys`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _authorized_keys__ref_identities:

authorized_keys__identities
---------------------------

The ``authorized_keys__*_identities`` variables are used to define a list of
"SSH Key identities". Each identity can use one or more SSH public keys and has
a corresponding list of UNIX accounts which will include the SSH keys of
a given identity, with optional configuration as specified in the
:man:`authorized_keys(5)` manual page (see "authorized_keys file format"
section for list of options).

By default the keys will be stored in the :file:`/etc/ssh/authorized_keys/`
directory, with separate file for each UNIX account. These files are owned by
``root`` and the corresponding user's UNIX group has read-only access to them,
to prevent modification by the users.

Alternatively, the account's :file:`~/.ssh/authorized_keys` file can be used,
but this location will not be protected from the user modifications.

Examples
~~~~~~~~

Ensure that given SSH public keys are present in the user file:

.. code-block:: yaml

   authorized_keys__identities:

     - name: 'identity1'
       sshkeys: [ 'ssh-rsa AAAAB3NzaC1yc2EAAAA...', 'ssh-rsa AAAAB3NzaC1yc2EAAAA...' ]
       comment: 'admin@example.org'
       accounts:
         - 'user1'

Add SSH public keys from the :command:`ssh-agent` service running on the
Ansible Controller (useful with smartcards):

.. code-block:: yaml

   authorized_keys__identities:

     - name: 'identity2'
       sshkeys: '{{ lookup("pipe","ssh-add -L | grep ^ssh || cat ~/.ssh/*.pub || true") }}'
       accounts:
         - 'user2'

Define two global SSH identities and add them to different UNIX accounts on
different hosts:

.. code-block:: yaml

   # ansible/inventory/group_vars/all/authorized_keys.yml
   authorized_keys__identities:

     - name: 'manager'
       url: 'https://github.com/user2.keys'

     - name: 'deployment'
       url: 'https://gitlab.com/user2.keys'

  # ansible/inventory/host_vars/webserver/authorized_keys.yml
  authorized_keys__host_identities:

    - name: 'manager'
      accounts:
        - name: 'application'
          home: True

    - name: 'deployment'
      accounts:
        - name: 'application'
          options: [ 'restrict', 'pty' ]
          command: '/usr/local/bin/rrsync -wo /home/application/'
          comment: 'Deployment account'

  # ansible/inventory/host_vars/database/authorized_keys.yml
  authorized_keys__host_identities:

    - name: 'manager'
      accounts:
        - 'postgres'

    - name: 'deployment'
      accounts:
        - name: 'postgres'
          options: [ 'restrict', 'pty' ]
          environment:
            APP_NAME: 'application1'
          command: '/usr/bin/psql application_db app_user'
          comment: 'Database management access'

Set SSH keys from a file on Ansible Controller as the only keys on a given user
account:

.. code-block:: yaml

   authorized_keys__identities:

     - name: 'identity3'
       sshkeys: '{{ lookup("file", "/path/to/user3.pub") }}'
       accounts:
         - name: 'user3'
           exclusive: True

A few examples from the :man:`authorized_keys(5)` manual page:

.. code-block:: yaml

   authorized_keys__identities:

     - name: 'john'
       comment: 'john@example.net'
       sshkeys: 'ssh-rsa AAAAB2...19Q=='
       accounts:

         - name: 'application'
           options:
             - 'from="*.sales.example.net,!pc.sales.example.net"'

    - name: 'dump-user'
      comment: 'example.net'
      sshkeys: [ 'ssh-rsa AAAAC3...51R==' ]
      accounts:

        - name: 'backup'
          command: 'dump /home'

    - name: 'permit-access'
      sshkeys: 'ssh-rsa AAAAB5...21S=='
      accounts:

        - name: 'account1'
          options:
            - 'permitopen="192.0.2.1:80"'
            - 'permitopen="192.0.2.2:25"'

        - name: 'account2'
          options:
            - 'permitlisten="localhost:8080"'
            - 'permitopen="localhost:22000"'

    - name: 'jane'
      sshkeys: 'ssh-rsa AAAA...=='
      accounts:

        - name: 'vpntunnel'
          comment: 'jane@example.net'
          options:
            - 'tunnel="0"'
          command: 'sh /etc/netstart tun0'

    - name: 'restricted-user'
      sshkeys:
        - 'ssh-rsa AAAA1C8...32Tv=='
        - 'ssh-rsa AAAA1f8...IrrC5=='
      comment: 'user@example.net'
      options:
        - 'restrict'
      accounts:

        - name: 'uptime'
          command: 'uptime'

        - name: 'games'
          options:
            - 'pty'
          command: 'nethack'

Setup a :man:`git-shell(1)` service for a specific SSH key identity on a given
UNIX account, with a custom :command:`gitserve` wrapper to support both
interactive and non-interactive operation:

.. literalinclude:: examples/gitserve
   :language: shell
   :lines: 1,6-

.. code-block:: yaml

   authorized_keys__identities:

     - name: 'git-deploy'
       url: 'https://github.com/username.keys'
       comment: 'Deployment identity'
       options:
         - 'restrict'
         - 'pty'
       command: '/usr/local/bin/gitserve'
       accounts:
         - 'application1'
         - 'application2'
         - 'application3'

Syntax
~~~~~~

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. A string which identifies an "SSH key identity", not used
  otherwise. Configuration entries with the same ``name`` parameter are merged
  during role execution and can affect each other. Most of the parameters in
  subsequent configuration entries will replace the former ones; exceptions are
  ``options``, ``environment`` and ``accounts`` parameters.

``sshkeys``
  String or a YAML list containing SSH public keys. If both ``sshkeys`` and
  ``url`` are specified, the former takes precedence.

``url``
  String containing an URL to a resource which returns a file with SSH public
  keys (only one URL is allowed at the moment). Be aware that SSH key sources
  not controlled directly can be modified at any time, in which case the role
  might lose track of SSH keys already present on the host.

``comment``
  Optional. String which will be added at the end of the SSH public key on all
  defined UNIX accounts, usually a comment about the key owner.

``state``
  Optional. If not specified or ``present``, a given SSH identity will be
  included in the list of generated identities. SSH keys will be added on any
  UNIX accounts defined in the ``accounts`` parameter. If ``absent``, known SSH
  keys will be removed from any defined UNIX accounts. If ``ignore``, a given
  configuration entry will not be processed by the role during execution.

``options``
  Optional. YAML list of :man:`authorized_keys(5)` key options which should be
  added to SSH keys added to all defined UNIX accounts. Mostly useful to add
  the ``restrict`` option to all SSH keys, which can then be augmented on
  a per-account basis. Values of the parametrized options need to include
  quotation marks. The ``environment=`` and ``command=`` options have separate
  parameters for special handling and should not be defined using the
  ``options`` parameter.  The ``options`` parameters from multiple
  configuration entries are merged together and can affect each other,
  depending on the ``state`` parameter.

``environment``
  Optional. YAML dictionary which specifies environment variables which should
  be set for a given SSH key. The variable names are defined as dictionary keys
  and their values as dictionary values. These environment variables will be
  set on all defined UNIX accounts; variable values can be overridden on
  a per-account basis.

``command``
  Optional. A string which will be defined as the ``command=`` option for given
  SSH keys on all specified UNIX accounts. Commands will be automatically
  quoted using double quotes (``""``) characters. The ``command`` parameter can
  be overridden on a per-account basis.

``accounts``
  Optional. List of UNIX accounts on which a given SSH identity should be
  configured. The ``accounts`` parameters from multiple configuration
  entries are merged together and can affect each other, depending on the
  ``state`` parameter.

  The list entries can be simple strings which will be interpreted as UNIX
  account names - in this case a given SSH identity will be configured in the
  :file:`/etc/ssh/authorized_keys/<account>` file. Alternative syntax using
  YAML dictionary with specific parameters described below can be used to
  modify SSH identity configuration on a per-account basis:

  ``name``
    Required. Name of the user account to configure. This will be used as the
    name of the file located in the :file:`/etc/ssh/authorized_keys/`
    directory. If needed, a corresponding UNIX group with the same name will be
    created to provide access to the file with SSH keys.

  ``state``
    Optional. If undefined or ``present``, the SSH public keys will be added to
    the user file. If ``absent``, the specified SSH public keys will be removed
    from the user file.

  ``comment``
    Optional. String which will be added at the end of the SSH public key,
    usually a comment about the key owner.

  ``options``
    Optional. YAML list of :man:`authorized_keys(5)` key options which should
    be added to SSH keys added to a given UNIX account. Values of the
    parametrized options need to include quotation marks. The ``environment=``
    and ``command=`` options have separate parameters for special handling and
    should not be defined using the ``options`` parameter.

  ``environment``
    Optional. YAML dictionary which specifies environment variables which
    should be set for a given SSH key on a given UNIX account. The variable
    names are defined as dictionary keys and their values as dictionary values.

  ``command``
    Optional. A string which will be defined as the ``command=`` option for
    given SSH keys on a given UNIX account. Commands will be automatically
    quoted using double quotes (``""``) characters.

  ``exclusive``
    Optional, boolean. If defined and ``True``, role will remove all other SSH
    public keys located in the user file and set only the SSH public keys present
    in the ``item.sshkeys`` or ``item.url`` parameters. Keep in mind that using
    this option can break idempotency if multiple entries with the same
    ``name`` parameter are used.

  ``home``
    Optional, boolean. If not specified or ``False``, the SSH keys will be
    managed in the :file:`/etc/ssh/authorized_keys/` directory, with custom
    access permissions. If ``True``, the SSH keys will be maintained in the
    :file:`~/.ssh/authorized_keys` file of a given UNIX account, if that
    account already exists.

  The parameters below are related to the files located in the
  :file:`/etc/ssh/authorized_keys/` directory:

  ``owner``
    Optional. Set the owner of the SSH identity file. If the owner account does
    not exist, ``root`` will become the owner.

  ``group``
    Optional. Name of the primary group of a given SSH identity file. If the
    specified group does not exist, it will be automatically created by the
    role.

    If the ``group`` parameter is not specified, the role will try to set the
    group of the file the same as the specified UNIX account in ``name``
    parameter with the assumption that the corresponding primary group exists.
    If it does not exist, the primary group of the SSH identity file will be
    ``root``.

  ``system``
    Optional, boolean. If undefined or ``True``, the group created by the role
    will be a "system" group, with GID < 1000. If ``False``, the created group
    will be a "normal" group with GID >= 1000. The existing groups are not
    modified.

  ``gid``
    Optional. Specify the GID a given group should use.

  ``mode``
    Optional. Set the mode of the SSH identity file. If not specified, mode
    ``0640`` will be set to allow read access to the UNIX group.

  ``file_state``
    Optional. If undefined or ``present``, the SSH identity file will be
    present. If ``absent``, the SSH identity file will be removed.
