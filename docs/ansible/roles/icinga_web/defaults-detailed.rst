Default variable details
========================

Some of ``debops.icinga_web`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _icinga_web__ref_modules:

icinga_web__modules
-------------------

The ``icinga_web__*_modules`` variables define what Icinga Web modules will be
installed by the role. The variables are merged together and each list entry
from the default list can be overwritten using the
:envvar:`icinga_web__modules` variable. List entries are YAML dictionaries with
specific parameters:

``name``
  Required. The name of the Icinga Web module. It will be used as the name of
  the symlink in the :file:`/usr/share/icingaweb2/modules/` directory.

  This parameter is also used as a marker for merging of different entries.

``git_repo``
  Optional. An URL of the :command:`git` repository which contains the module.
  External modules will be cloned to the :file:`/usr/local/src/icinga_web/`
  directory with subdirectories based on their URL.

``git_version``
  Optional. Specify the version (tag) or branch of a given module to install.

``enabled``
  Optional, boolean. If ``True``, the module will be enabled by default. If
  ``False``, module will be disabled but can still be enabled via the web
  interface.

``state``
  Optional. Specify the desired state of the module. If ``present``, the module
  will be installed and enabled. If ``absent``, existing modules will be
  disabled but not removed entirely; non-installed modules won't be installed.

Examples
~~~~~~~~

See the :envvar:`icinga_web__default_modules` variable for examples.


.. _icinga_web__ref_initial_account_groups:

icinga_web__initial_account_groups
----------------------------------

The :envvar:`icinga_web__initial_account_groups` variable defines a list of
account groups added to the Icinga Web database during initialization. The list
is ordered sequentially and groups are numbered from 1, therefore the first
group listed should be "Administrators".

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of the group to create.

``state``
  Optional. If not specified or ``present``, the group will be created in the
  database. If ``absent``, the group will not be created.

Examples
~~~~~~~~

See the :envvar:`icinga_web__initial_account_groups` variable for examples.


.. _icinga_web__ref_initial_accounts:

icinga_web__initial_accounts
----------------------------

The :envvar:`icinga_web__initial_accounts` variable defines a set of
administrator accounts added to the Icinga Web database during initialization.
These accounts allow users to login to the web interface and use the Icinga
Director REST API. All accounts listed will be added to the account grup with
id ``1``, ie. the first one created, usually "Administrators".

Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. The name of the user account to add to the database.

``state``
  Optional. If not specified or ``present``, the account will be added to the
  database. If ``absent``, the account will not be created during
  initialization.

``password``
  Optional. A plaintext password which will be hashed and encoded in the format
  expected by Icinga Web application and stored in the database.

  If not specified, the value of the
  :envvar:`icinga_web__default_account_password` variable will be used by
  default.

``password_hash``
  Optional. A hash of the password to store in the database for a given user
  account. Icinga 2 Web uses `native password hashing from PHP 5.6+`__ and the
  password hash should be specified in this format.

  .. __: https://www.icinga.com/docs/icingaweb2/latest/doc/20-Advanced-Topics/#advanced-authentication-tips

``group_id``
  Optional. Specify the numeric group id to which a given account should be
  added. If not specified, ``1`` is used by default.

Examples
~~~~~~~~

See the :envvar:`icinga_web__initial_accounts` variable for examples.


.. _icinga_web__ref_ini_configuration:

icinga_web__ini_configuration
-----------------------------

The :ref:`debops.icinga_web` role uses a set of default variables to create and
maintain the INI configuration files of Icinga 2 Web application, located in
the :file:`/etc/icingaweb2/` directory. Because these files can be modified
through the Web interface, the role combines the current configuration gathered
at runtime from the host with the default configuration defined by the role and
custom user configuration defined in the Ansible inventory variables.

Each set of variables maintains one INI configuration file. The variables are
defined as list of INI configuration sections with options defined as keys and
values. Each section is defined using specific parameters:

``name``
  Required. The INI section name. This variable is used as a marker to merge
  multiple configuration entries together.

``state``
  Optional. If not specified or ``present``, a given configuration section will
  be included in the generated file. If ``absent``, a given configuration
  section will be removed from the generated file. If ``ignore``, a given
  configuration entry will be ignored by the role and not evaluated.

``options``
  Optional. Specify the INI configuration options in a given section. The
  ``options`` lists from multiple configuration entries with the same ``name``
  are merged together, this allows to modify existing options or add new ones
  seamlessly.

  Each element of the list is a YAML dictionary with specific parameters:

  ``name``
    Required. The option name.

  ``value``
    Required. The option value.

  ``state``
    Optional. If not specified or ``present``, the option will be included in
    the generated file. If ``absent``, the option will be removed from the
    generated file. If ``ignore``, the given element will not be evaluated by
    the role.

Examples
~~~~~~~~

See the :envvar:`icinga_web__default_config` or the
:envvar:`icinga_web__default_resources` variables for example usage.
