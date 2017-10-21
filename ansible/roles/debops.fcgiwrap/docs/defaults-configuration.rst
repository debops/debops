Default variables: configuration
================================

some of ``debops.fcgiwrap`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1

.. _fcgiwrap__instances:

fcgiwrap__instances
-------------------

List of ``fcgiwrap`` user instances, each one defined by a YAML dictionary.
These instances will configure system services (init scripts on ``sysvinit``
and units on ``systemd``) which will start ``fcgiwrap`` unprivileged on
specified user account.

List of known parameters:

``name``
  Required. Name of the instance, will be used as the name of the init
  scripts/unit files and socket.

``user``
  Required. Name of the user account to use for this instance.

``group``
  Primary group of a given user account to use for this instance.

``home``
  Path to the home directory for the user account. If account does not exist,
  it will be created automatically with specified home directory.

``createhome``
  Boolean, by default ``False``. Specify if the user home directory should be
  created if it does not exist.

``shell``
  Shell used by specified user account.

``system``
  Boolean, by default ``True``. If the account does not exist, it will be
  created as a "system" account with its UID/GID < 1000.

``socket_user``
  Owner of the socket used by this ``fcgiwrap`` instance.

``socket_group``
  Group which has access to this instance's socket.

``socket_mode``
  File permissions set on this instance's socket.

