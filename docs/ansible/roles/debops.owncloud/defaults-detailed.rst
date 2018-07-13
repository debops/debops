Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.owncloud`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _owncloud__ref_config:

owncloud__config
----------------

Dict keys can be overridden when they are present in multiple dicts.
Order of priority from least to most specific:

* :envvar:`owncloud__role_config`
* :envvar:`owncloud__role_recommended_config`
* :envvar:`owncloud__config`
* :envvar:`owncloud__group_config`
* :envvar:`owncloud__host_config`

Each variable can hold multiple keys and values. The dict value can either be a
value directly intended for ownCloud (corresponding directly to the value in
the :file:`config.php` file) or a dict itself in case more flexibility is
required. A ownCloud value can also be a dict. The decision is made based on
the presence of the ``value`` and the ``state`` keys. If both are present, the
``state`` key will be evaluated by Ansible.
Here are the available options of the inner dict:

``value``
  Required, string. Corresponding to the value in the :file:`config.php` file.

``state``
  Required, string. Allows to specify if the option should be ``present`` or ``absent`` in the configuration.

.. note:: Parameters with \ (backslash) need to be double escaped:

   .. code:: yaml

      owncloud__config:
        memcache.local: '\\OC\\Memcache\\APCu'

  This is not confirmed by the `official ownCloud documentation
  <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/caching_configuration.html>`_
  but is a result of how the configuration file is generated using JSON as intermediate data format.

Refer to the `official ownCloud documentation <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/config_sample_php_parameters.html>`__ for details about the available configuration options.

Change/Disable skeleton files for new users (example)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The skeleton files which new users get copied into there ownCloud profile on
first login can be changed by the ``skeletondirectory`` setting which points to
the skeleton directory to use.

In case users should primarily stored their files on external storage, it can
make sense to not provided any skeleton files at all. This can be archived by
putting:

.. code-block:: yaml

   owncloud__config:

     ## Points to the skeleton directory to use on first login of users.
     ## If this setting is an empty string, no files will be provided by default.
     skeletondirectory: ''

into your Ansible inventory.


.. _owncloud__ref_owncloud__user_files:

owncloud__user_files
--------------------

This section describes the options of :envvar:`owncloud__user_files` and
similar lists.

Each list item is a dict with the following keys:

``src``
  Path to the source file on the Ansible Controller. Alternatively you can use
  ``content`` to provide the file contents directly in the inventory.

``content``
  String or YAML text block with the file contents to put in the destination
  file. Alternatively you can use ``src`` to provide the path to the
  source file on Ansible Controller.

``dest``
  Required, string. Path of the destination. The first directory is the user id.
  Example: :file:`user_id/files/path`.
  The destination on the remote host will be ``owncloud__data_path + "/" + item.dest``.

``state``
  Optional. If not specified, or if specified and ``present``, the file(s) will
  be created. If specified and ``absent``, file will be removed.

Additionally, all parameters of the `Ansible copy module`_ are supported.

The reason why these lists exist (instead of using :ref:`debops.resources`) is that
ownCloud needs to be aware of any changes.

Examples
~~~~~~~~

Provide an immutable :file:`README.md` file in the root directory of the ownCloud admin user:

.. code-block:: yaml

   owncloud__user_files_group:

     - dest: '{{ owncloud__admin_username }}/files/README.md'
       content: |
         This ownCloud instance is managed by Ansible.
         Changes done via the ownCloud web interface might be overwritten
         by subsequent Ansible runs.
         Refer to https://docs.debops.org/en/latest/ansible/roles/debops.owncloud/index.html for details.
       owner: 'root'
       group: 'root'


Provide an :file:`README.md` file in the :file:`project_a` subdirectory of the ownCloud admin user.
The :file:`project_a` directory will be created if it does not already exist.
The ownCloud admin user can change/delete the file and directory:

.. code-block:: yaml

   owncloud__user_files_group:

     - dest: '{{ owncloud__admin_username }}/files/project_a/README.md'
       content: |
         File template.
         Changes done to this file will be overwritten by subsequent Ansible runs.


.. _owncloud__ref_post_upgrade_hook:

owncloud__post_upgrade_hook_list
--------------------------------

Each element of the  :envvar:`owncloud__post_upgrade_hook_list` list either
is a simple string of the script‘s file path or a dict with the following options:

``path``
  Optional, string. File path of the script.

``state``
  Required, string. Allows to specify if upgrade hook script should be invoked
  (``present``) or ignored (``absent``) during after the upgrade.
