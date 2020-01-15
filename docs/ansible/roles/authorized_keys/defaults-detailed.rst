Default variable details
========================

Some of ``debops.authorized_keys`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _authorized_keys__ref_list:

authorized_keys__list
---------------------

The :envvar:`authorized_keys__list`, :envvar:`authorized_keys__group_list`,
:envvar:`authorized_keys__host_list` and :envvar:`authorized_keys__dependent_list`
variables are used to define what SSH keys should be present in each user
file located in :file:`/etc/ssh/authorized_keys/` directory. Each list entry is
a YAML dictionary with specific parameters:

``name``
  Required. Name of the user account to configure. This will be used as the
  name of the file located in the :file:`/etc/ssh/authorized_keys/` directory.

These parameters are related to SSH public key management:

``sshkeys``
  Optional. String containing either a SSH public key, or an URL to a resource
  which returns a file with SSH public keys (only one URL is allowed at the
  moment), or a YAML list of SSH public keys.

``github``
  Optional. String with the name of a GitHub account. SSH public keys belonging
  to this account will be added to, or removed from, the specified user file.
  The SSH keys will be downloaded from: ``https://github.com/<username>.keys``
  Only one GitHub account is allowed at a time.

``options``
  Optional. String or list of SSH options which should be set for each key
  specified on the ``sshkeys`` list. You can find more about available options
  in :man:`authorized_keys(5)`.

  If this parameter is not specified, SSH public keys will use options set in
  the :envvar:`authorized_keys__default_options` variable. To override this variable
  for a particular entry, set the ``item.options`` parameter as empty string or
  list.

  The specified SSH key options are applied to all keys specified in the
  ``sshkeys`` or ``github`` parameters in this specific entry. To use different
  key options for different SSH keys, specify them in separate entries on the
  list.

``key_options``
  Optional. Additional set of options to add to the SSH public keys. This can
  be used with ``item.options`` parameter to easily combine a list of options
  from another variable with a custom additional options. For example:

  .. code-block:: yaml

     authorized_keys__list:
       - name: 'user'
         github: 'user'
         options: '{{ authorized_keys__options_map.strict }}'
         key_options: 'command="ls -l /home/user"'

``exclusive``
  Optional, boolean. If defined and ``True``, role will remove all other SSH
  public keys located in the user file and set only the SSH public keys present
  in the ``item.sshkeys`` or ``item.github`` parameters.

``state``
  Optional. If undefined or ``present``, the SSH public keys specified in the
  ``item.sshkeys`` or ``item.github`` parameters will be added to the user
  file. If ``absent``, the specified SSH public keys will be removed from the
  user file.

These parameters are related to the files located in the
:file:`/etc/ssh/authorized_keys/` directory:

``readonly``
  Optional, boolean. If defined and ``True``, or if the corresponding
  :envvar:`authorized_keys__readonly` variable is ``True``, the role will set the
  owner and group of the user file as ``root:<item.group|primary group of user|root>`` and
  its permissions will be set to ``0640``, so that the respective users being
  in their own groups can still access the file and use it for authentication,
  but they cannot change it.

  If this parameter is set to ``False`` or the corresponding
  :envvar:`authorized_keys__readonly` variable is ``False``, to role will not modify
  the file ownership or permissions set by the ``authorized_key`` Ansible
  module.

``owner``
  Optional. Set the owner of the user file. If the owner account does not
  exist, ``root`` will become the owner.

``group``
  Optional. Name of the primary group of a given user file. If the specified
  group does not exist, it will be automatically created by the role.

  If the ``item.group`` parameter is not specified, the role will try to set
  the group of the file the same as the specified user in ``item.name``
  parameter with the assumption that the corresponding primary group exists. If
  it does not exist, the primary group of the user file will be ``root``.

``system``
  Optional, boolean. If undefined or ``True``, the group created by the role
  will be a "system" group, with GID < 1000. If ``False``, the created group
  will be a "normal" group with GID >= 1000. The existing groups are not
  modified.

``gid``
  Optional. Specify the GID a given group should use.

``mode``
  Optional. Set the mode of the user file. If not specified, mode ``0640`` or
  ``0600`` will be set depending on read only configuration parameters.

``file_state``
  Optional. If undefined or ``present``, the user file will be present. If
  ``absent``, the user file will be removed.

Examples
~~~~~~~~

Ensure that given SSH public keys are present in the user file:

.. code-block:: yaml

   authorized_keys__list:
     - name: 'user1'
       sshkeys: [ 'ssh-rsa AAAAB3NzaC1yc2EAAAA...', 'ssh-rsa AAAAB3NzaC1yc2EAAAA...' ]

Add SSH public keys from specified URL:

.. code-block:: yaml

   authorized_keys__list:
     - name: 'user2'
       sshkeys: 'https://auth.example.com/api/ssh/user2'

Add SSH keys from two GitHub accounts to specified user account:

.. code-block:: yaml

   authorized_keys__list:

     - name: 'app1'
       github: 'user-one'

     - name: 'app1'
       github: 'user-two'

Set SSH keys from a file on Ansible Controller as the only keys on a given user
account:

.. code-block:: yaml

   authorized_keys__list:
     - name: 'user3'
       sshkeys: '{{ lookup("file", "/path/to/user3.pub") }}'
       exclusive: True
