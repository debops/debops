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
Order of priority from least specific to most specific:

* :envvar:`owncloud__config_role_required`
* :envvar:`owncloud__config_role_optional`
* :envvar:`owncloud__config`
* :envvar:`owncloud__config_group`
* :envvar:`owncloud__config_host`

Each dict can hold multiple keys and values. The dict value can either be a
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
