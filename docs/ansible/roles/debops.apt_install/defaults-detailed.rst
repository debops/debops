Default variable details
========================

.. include:: ../../../includes/global.rst

Some of ``debops.apt_install`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. contents::
   :local:
   :depth: 1

.. _apt_install__ref_debconf:

apt_install__debconf
-------------------------

These YAML lists can be used to add some values to Debconf database. Each entry
has the same keys as the ones used by `Ansible debconf module`_. See its
documentation for parameter advanced usage and syntax.

``name``
  Required. Name of the package to configure.

``question``
  A debconf configuration setting.

``unseen``
  Do not set 'seen' flag when pre-seeding.

``value``
  Value to set the configuration to.

``vtype``
  The type of the value supplied.

Examples
~~~~~~~~

Define the path to Matlab installation for matlab-support :

.. code-block:: yaml

   apt_install__debconf:
     - name: 'matlab-support'
       question: 'matlab-support/matlab-install-glob'
       value: '/usr/local/MATLAB/R2018b'
       vtype: 'string'

.. _apt_install__all_packages:

apt_install__all_packages
-------------------------

This variable holds all YAML lists used by the corresponding Ansible lookup
template passed to the :command:`apt` module. Each element of this list can specify
a name of the APT package to install, or a list of packages, or a YAML
dictionary which defines conditions for the installation of the package(s).

The different dictionary keys that can be used to specify conditional
installation:

``name``
  Required. Name of the APT package, or YAML list of package names to install.

``state``
  Optional. Specify if the given package(s) should be included in the list of
  packages to install (not the status of installation). If not specified or
  ``present``, package(s) will be included, if ``absent``, packages won't be
  included.

``distribution``
  Optional. Name or list of operating system distributions. If specified,
  a given package or list of packages will be installed only on these
  distributions.

``release``
  Optional. Name or list of distribution release names. If specified, a given
  package or list of packages will be installed only on systems with given OS
  releases.

``area``
  Optional. Name or list of package archive areas (``main``, ``non-free``,
  ``restricted``, etc.). If specified, role will check if a given archive area
  is enabled using Ansible local facts. The specified package(s) will be
  installed only when a given area is available. This can be used to avoid
  errors with missing packages on systems where non-free archive areas are not
  enabled.

``whitelist``
  Optional. This variable should reference a list of package names. The lookup
  template that filters the list of packages for installation will compare the
  names of selected packages against this list, and only packages which are
  included will be installed. This is used to provide an alternative, easier
  way to select packages for installation without the need to modify a huge,
  conditional list.

Examples
~~~~~~~~

Install packages on any OS release:

.. code-block:: yaml

   apt_install__packages:
     - 'package1'
     - 'package2'

Install packages only when specified OS release is present:

.. code-block:: yaml

   apt_install__packages:
     - name: 'package1'
       release: [ 'wheezy', 'trusty' ]

Install packages only when specified archive area is available:

.. code-block:: yaml

   apt_install__packages:
     - name: 'package1'
       area: 'non-free'

Install packages using Ansible fact condition:

.. code-block:: yaml

   apt_install__packages:
     - name: [ 'package1', 'package2' ]
       state: '{{ "present"
                  if (ansible_virtualization_role == "guest")
                  else "absent" }}'


.. _apt_install__ref_alternatives:

apt_install__alternatives
-------------------------

These YAML lists can be used to configure special symlinks (for example,
``editor``, ``x-terminal-emulator``, ``pager``) which can point to different
applications that provide similar functionality using the
``update-alternatives`` command. Each list element is a YAML dictionary with
specific parameters:

``name``
  Required. Name of the symlink which should be configured.

``path``
  Optional. Absolute path to the application which should be symlinked. To see
  available alternatives, you can run the command:

  .. code-block:: console

     update-alternatives --display <name>

  If the ``path`` parameter is not specified, the role will configure a given
  symlink to select an application automatically.

``link``
  Optional. Absolute path to the file which should be symlinked. This is rarely
  needed.

``priority``
  Optional. Set a priority for a given application package. This is rarely
  needed.

Examples
~~~~~~~~

Configure Emacs to be the default system editor:

.. code-block:: yaml

   apt_install__alternatives:
     - name: 'editor'
       path: '/usr/bin/emacs24'

Let the system decide automatically what editor to use as default:

.. code-block:: yaml

   apt_install__alternatives:
     - name: 'editor'
