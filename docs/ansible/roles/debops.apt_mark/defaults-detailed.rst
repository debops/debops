Default variable details
========================

Some of ``debops.apt_mark`` default variables have more extensive configuration
than simple strings or lists, here you can find documentation and examples for
them.

.. contents::
   :local:
   :depth: 1


.. _apt_mark__ref_packages:

apt_mark__packages
------------------

The ``apt_mark__*_packages`` list variables specify the desired state of the
APT packages to set on the hosts. Only already installed APT packages are
managed. Each list entry is a YAML dictionary with specific parameters:

``name``
  Required. Name of an APT package to configure. At the moment the role does
  not support usage of glob patterns (eg. ``package-*``).

``packages``
  Optional. A list of APT packages to manage. If specified, the ``name``
  parameter is ignored. Glob patterns are not supported.

``state``
  Optional. This parameter defines what state to set for the specified
  package(s) The available states:

  +------------+-----------------+-------------------+
  |            | ``auto``        | ``manual``        |
  +------------+-----------------+-------------------+
  | ``hold``   | ``auto-hold``   | ``manual-hold``   |
  +------------+-----------------+-------------------+
  | ``unhold`` | ``auto-unhold`` | ``manual-unhold`` |
  +------------+-----------------+-------------------+

  If not specified, ``manual`` state is set by default, hold state is not
  changed. You can find out more about these states in the :man:`apt-mark(8)`
  manual page.

Examples
~~~~~~~~

Mark a package as installed manually, so it won't be autoremoved:

.. code-block:: yaml

   apt_mark__packages:

     - name: 'zsh'

     - name: 'bash'
       state: 'manual'

Mark multiple installed packages as installed manually and held in their
current state. Only the packages already installed will be affected:

.. code-block:: yaml

   apt_mark__packages:

     - name: 'nginx-packages'
       state: 'manual-hold'
       packages:
         - 'nginx'
         - 'nginx-common'
         - 'nginx-extras'
