.. _gunicorn__ref_defaults_detailed:

Default variable details
========================

.. include:: includes/all.rst

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
with either a string, a YAML list or a YAML dictionary as values. See

``working_dir``
  Required, string. Path to the working directory of a given application.

``python``
  Optional, string. Path to the Python executable to use.

``mode``
  Optional, string. What mode to use for the application, usually ``wsgi`` or
  ``django``.

``user``
  Optional, string. UNIX user account which will be used to run the application
  processes. If not specified, ``www-data`` user account will be used.

``group``
  Optional, string. UNIX group which will be used to run the application
  processes. If not specified, ``www-data`` group will be used.

``environment``
  Optional. YAML dictionary with environment variables to set for a given
  application. Each dictionary key should be the variable name, and dictionary
  value will be its value.

``args``
  Required. YAML list of arguments to pass to the ``gunicorn`` daemon.

Examples
~~~~~~~~

.. literalinclude:: examples/gunicorn-applications.yml
   :language: yaml
