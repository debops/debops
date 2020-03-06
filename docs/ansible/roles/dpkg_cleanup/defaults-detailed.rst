.. Copyright (C) 2020 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2020 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Default variable details
========================

Some of the ``debops.dpkg_cleanup`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1


.. _dpkg_cleanup__ref_packages:

dpkg_cleanup__packages
----------------------

The ``dpkg_cleanup__*_packages`` list variables (currently a single one) define
what files should be removed or reverted by the ``pre-invoke`` hook script.

Examples
~~~~~~~~

Remove additional files and restart a service before the ``application``
package is removed:

.. code-block:: yaml

   application__dpkg_cleanup__dependent_packages:
     - name: 'application'
       remove_files:
         - '/path/to/custom/file'
         - '/path/to/other/file'
       restart_services:
         - 'other-service'

Syntax
~~~~~~

Each entry in the list is a YAML dictionary with specific parameters:

``name``
  Required. The name of the Debian or Ubuntu package which will trigger the
  cleanup script.

``state``
  Optional. If not specified or ``present``, the cleanup hook and script will
  be created on the host. If ``absent``, the hook and script will be removed
  from the host.

``ansible_fact``
  Optional. By default the cleanup script will remove the corresponding Ansible
  local fact based on the Debian or Ubuntu package name. If the fact has
  a different name, you can use this parameter to specify it, including the
  ``.fact`` suffix.

``revert_files``
  Optional. A single file defined as a string, or a list of files. When the
  cleanup script is triggered, it will check if a corresponding file with the
  ``.dpkg-divert`` suffix is present in the filesystem. If it is found, the
  script will remove the changed file without the ``.dpkg-divert`` suffix, and
  use the :manpage:`dpkg-divert(1)` command to revert the original file in its
  place. For security, only absolute paths are allowed.

``remove_files``
  Optional. A single file defined as a string, or a list of files. When the
  cleanup script is triggered, the specified files will be removed. For
  security, only absolute paths are allowed.

  The role will automatically include the hook and script files, as well as the
  Ansible local fact script based on the name of the Debian package, so they
  don't need to be specified separately.

``remove_directories``
  Optional. A single directory defined as a string, or a list of directories.
  When the cleanup script is triggered, the specified directories will be
  removed. For security, only absolute paths are allowed.

``reload_services``
  Optional. A single :command:`systemd` service or a list of services. When the
  cleanup script is triggered, it will run the :command:`systemctl reload`
  command for each service specified in this parameter. This can be used to
  update runtime configuration of system services, for example remove firewall
  rules that were used by a service.

``restart_services``
  Optional. A single :command:`systemd` service or a list of services. When the
  cleanup script is triggered, it will run the :command:`systemctl restart`
  command for each service specified in this parameter. This can be used to
  update runtime configuration of system services, for example remove firewall
  rules that were used by a service.
