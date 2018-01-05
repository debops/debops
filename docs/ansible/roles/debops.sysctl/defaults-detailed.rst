Default variable details
========================

Some of ``debops.sysctl`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _sysctl__ref_parameters:

sysctl__parameters
------------------

The :envvar:`sysctl__parameters` and included dictionaries allow to specify kernel parameters.
The key of the dictionary is the dot-separated path (aka `key`) specifying the
sysctl variable. The value of the dict is either a string with the desired
value of the sysctl key or a dict itself with the following options:

``value``
  Required. Desired value of the sysctl key.

``comment``
  Optional. A string or YAML text block with comments about the given
  parameter, will be included in the generated configuration file.

``state``
  Optional, string. Defaults to ``present``. ``present`` will cause the kernel
  parameter to be set.  If ``absent`` the kernel parameter will not be
  influenced.
