.. Copyright (C) 2026 seven-beep <ebn@entreparentheses.xyz>
..  Copyright (C) 2026 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only


Default variable details
========================

Some of ``debops.needrestart`` default variables have more extensive
configuration than simple strings or lists, here you can find documentation and
examples for them.

.. only:: html

   .. contents::
      :local:
      :depth: 1

.. _needrestart__ref_configuration:

needrestart__configuration
------------------------------

:envvar:`needrestart__configuration` and similar dictionary variables
can be used to manage the configuration of :program:`needrestart`.

The dictionary key is the filename that would be templated in :file:`/etc/needrestart/conf.d/`.
This allows to mask/overwrite them later in the hierarchy as defined by :envvar:`needrestart__combined_configuration`.
For use as dependency role, the key should be ``{{ weight }}_{{ role_owner }}_{{ role_name }}{{ optional_tags }}``
where ``weight`` should be a two-digit number. For DebOps roles, the weight ``50`` should be used.

Each dictionary value is a dictionary by itself with the following supported options:

``content``
  Required, string. Raw needrestart configuration.

``state``
  Optional, string. Defaults to ``present``
  Options:

  ``present``
  The configuration file should be installed.

  ``absent``
  The configuration file should be removed if it exists.

  ``ignore``
  The configuration file should ignored by the role.

``by_role``
  Optional, string. Name of the Ansible role in the format
  ``{{ role_owner }}.{{ role_name }}`` which is responsible for the entry.
  This option probably only makes sense in the use as dependency role.

.. _needrestart__ref_restart_scripts:

needrestart__restart_scripts
----------------------------

These lists can be used to manage content or copy files from the Ansible
Controller in the :file:`/etc/needrestart/restart.d` of remote hosts. Each
element of a list is a YAML dictionary with parameters used by the `Ansible
ansible.builtin.copy module`_. See its documentation for parameter advanced
usage and syntax.

.. _Ansible ansible.builtin.copy module: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html

Here are some more important parameters:

``filename`` or ``name``
  Required. Path to the destination file on the remote host.

``src``
  Path to the source file on the Ansible Controller. Alternatively you can use
  ``item.content`` to provide the file contents directly in the inventory.

``content``
  String or YAML text block with the file contents to put in the destination
  file. Alternatively you can use ``item.src`` to provide the path to the
  source file on Ansible Controller.

``state``
  Optional. If not specified, or if specified and ``present``, the file(s) will
  be created. If specified and ``absent``, file will be removed.

``divert``
 Optional, boolean.
 Allow to divert a script that was installed by :program:`needrestart`.
