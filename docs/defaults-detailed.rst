Default variable details
========================

.. include:: includes/all.rst

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

  This is not confirmed by the `official ownCloud Dokumentation
  <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/caching_configuration.html>`_
  but is a result of how the configuration file is generated using JSON as intermediate data format.

Refer to the `official ownCloud Dokumentation <https://doc.owncloud.org/server/9.0/admin_manual/configuration_server/config_sample_php_parameters.html>`__ for details about the available configuration options.

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

.. _owncloud__ref_updates_post_hook_scripts:

updates_post_hook_scripts
-------------------------

Each element of the  :envvar:`owncloud__upgrade_post_hook_scripts` list either
is a simple string of the script‘s file path or a dict with the following options:

``path``
  Optional, string. File path of the script.

``state``
  Required, string. Allows to specify if upgrade hook script should be invoked
  (``present``) or ignored (``absent``) during after the upgrade.
