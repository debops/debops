.. _rstudio_server__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.rstudio_server`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1


.. _rstudio_server__ref_allow_users:

rstudio_server__allow_users
---------------------------

The ``rstudio_server__*_allow_users`` variables define a list of UNIX user
accounts that should be added to the system group defined by the
:envvar:`rstudio_server__auth_group`. Accounts in this group will be able to
login to the RStudio Server web application. Only already existing UNIX
accounts will be added to the group, role does not create them automatically.

Each list entry can be a string containing an account name, or a YAML
dictionary with specific parameters:

``name``
  The name of the UNIX account to include in the auth group.

``state``
  Optional. If not specified or ``present``, the account will be added to the
  auth group.

Examples
~~~~~~~~

Allow specific UNIX accounts access to RStudio Server:

.. code-block:: yaml

   rstudio_server__allow_users:
     - 'user1'
     - name: 'user2'


.. _rstudio_server__ref_conf:

rstudio_server__*_conf
----------------------

These variables specify the contents of the RStudio Server configuration files,
located in :file:`/etc/rstudio/` directory. Each variable is a list with YAML
dictionaries. Each entry can be written in a simple form where YAML dictionary
key is the option name, and the value is the option value. More complex form
can be defined using the parameters:

``name``
  The name of the option to set.

``value``
  The value of the option to set. If it's empty, it will be removed from the
  configuration file.

``state``
  Optional. If not specified or ``present``, the option will be added in the
  configuration file. If ``absent``, the option won't be included in the
  configuration file.

Examples
~~~~~~~~

Define options in the :file:`rserver.conf` configuration file:

.. code-block:: yaml

   rstudio_server__rserver_conf:

     - 'www-address': '127.0.0.1'

     - name: 'www-port'
       value: '8787'
