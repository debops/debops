.. _gunicorn__ref_defaults_detailed:

Default variable details
========================

Some of ``debops.gunicorn`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _gunicorn__ref_applications:

gunicorn__applications
----------------------

The :envvar:`gunicorn__applications` and
:envvar:`gunicorn__dependent_applications` lists manage the information about
the WSGi-compatible applications served by Gunicorn. Each entry is a YAML
dictionary with specific parameters. Most of the parameters are passed directly
to the configuration file after some processing.

List of known parameters:

``name``
  Required. Name of the application server to use, it will be used as the
  configuration file name in the :file:`/etc/gunicorn.d/` directory, as well as the
  process name.

``comment``
  Optional. Additional comments added to the beginning of the configuration
  file; can be specified as a string or a YAML text block.

``state``
  Optional. If not specified or ``present``, the configuration file will be
  generated. If ``absent``, the configuration file will be removed.

The rest of the parameters specified in a given entry should be dictionary keys
with either a string, a YAML list or a YAML dictionary as values.

``working_dir``
  Required, string. Path to the working directory of a given application.

``python``
  Optional, string. Path to the Python executable to use. If not specified, the
  system Python version will be used.

``binary``
  Optional, string. Either ``gunicorn`` (default) or ``gunicorn3`` to run Python 3
  compatible applications.

``mode``
  Optional, string. What mode to use for the application, usually ``wsgi`` or
  ``django``. This is only relevant on the older OS releases.

``user``
  Optional, string. UNIX user account which will be used to run the application
  processes. If not specified, ``www-data`` user account will be used. The role
  will create the user account if it doesn't exist, as long as the ``home``
  parameter is also specified.

``group``
  Optional, string. UNIX group which will be used to run the application
  processes. If not specified, ``www-data`` group will be used. The role will
  create the group if it doesn't exist.

``home``
  Optional, string. The absolute path of the application account home
  directory. Required for automatic account creation.

``system``
  Optional, boolean. If not specified or ``True``, the created UNIX account and
  group will be a system variant, with UID/GID <1000, which is typical for UNIX
  services.

``environment``
  Optional. YAML dictionary with environment variables to set for a given
  application. Each dictionary key should be the variable name, and dictionary
  value will be its value.

``args``
  Required. YAML list of arguments to pass to the ``gunicorn`` daemon. The last
  element of the list should be an application "entry point" module.

The next set of dictionary keys contains less used parameters, which can be
used to modify the internal service configuration.

``bind``
  Optional. Specify either a UNIX socket path as ``unix:/path/to/socket``, or
  a TCP socket in the form of ``ipaddr:port`` (the role does not configure
  firewall).

  If not specified, the role will configure an UNIX socket in the path:

  .. code-block:: none

     /run/gunicorn-<name>/<name>.sock

  The socket directory will be created with the ``item.user`` parameter as the
  UNIX account owner, and ``item.group`` as the UNIX account group.

  On older OS releases, the socket will be created as:

  .. code-block:: none

     /run/gunicorn/<name>.sock

``bind_mode``
  Optional. Specify the file mode of the UNIX socket directory. If not
  specified, ``0755`` is used by default

``pidfile``
  Optional. Specify an absolute path to the file with the PID of the main Green
  Unicorn process.

  If not specified, the role will create a PID file in the path:

  .. code-block:: none

     /run/gunicorn-<name>/<name>.pid

  On older OS releases, the PID file will be created as:

  .. code-block:: none

     /run/gunicorn/<name>.pid

``backlog``
  Optional. Maximum number of clients that are allowed to connect, usually
  between 64-2048. Clients that exceed this number will receive a connection
  error.

Examples
~~~~~~~~

.. literalinclude:: examples/gunicorn-applications.yml
   :language: yaml
