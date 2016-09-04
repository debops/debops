Default variable details
========================

.. include:: includes/all.rst

Some of ``debops.sysctl`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _sysctl__ref_parameters:

sysctl__parameters
------------------

The ``sysctl__parameters`` and included dictionaries allow to specify kernel parameters.
The key of the dictionary is the dot-separated path (aka `key`) specifying the
sysctl variable. The value of the dict is either a string with the desired
value of the sysctl key or a dict itself with the following options:

``value``
  Required. Desired value of the sysctl key.

``comment``
  Optional, string. Can be used for documentation. Currently not written
  anywhere.

``state``
  Optional, string. Defaults to ``present``. ``present`` will cause the kernel
  parameter to be set.  If ``absent`` the kernel parameter will not be
  influenced.

``reload``
  Optional, boolean. Defaults to :envvar:`sysctl__reload`.

``ignoreerrors``
  Optional, boolean. Defaults to :envvar:`sysctl__ignoreerrors`.

``sysctl_set``
  Optional, boolean. Defaults to ``False``.
  Verify token value with the :command:`sysctl` command and set with ``sysctl -w`` if
  necessary.
