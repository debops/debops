.. Copyright (C) 2023 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2023 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-only

Getting started
===============

.. only:: html

   .. contents::
      :local:


Support for other DNS resolvers
-------------------------------

The role checks if one of the APT packages listed in the
:envvar:`resolved__skip_packages` variable is already installed on the host
before doing any modification on the system. If such package is detected, the
role will skip further tasks to avoid messing up existing configuration.


Fallback DNS configuration
--------------------------

Since Debian 12 (Bookworm), the :command:`systemd-resolved` service is provided
via a separate package, which on installation automatically replaces the
:file:`/etc/resolv.conf` file with a symlink. The default Debian installation
still uses the ``ifupdown`` package to configure networking, which results in
broken DNS resolution on :command:`systemd-resolved` installation because the
service does not get the relevant nameserver information from ``ifupdown``
scripts.

To mitigate this, the :ref:`debops.resolved` role will get the current DNS
configuration from Ansible facts and add it in the
:file:`/etc/systemd/resolved.conf.d/00fallback-dns.conf` file as "Fallback DNS
configuration" before installing the service itself. This should avoid issues
with DNS before the actual configuration is defined. The file can be safely
removed later, or its configuration will be overridden if specified in the
subsequent configuration files.


Management of the :file:`/etc/resolv.conf` config file
------------------------------------------------------

The :file:`/etc/resolv.conf` configuration file can be overwritten by the
:command:`dhclient` command, used by the ``ifupdown`` scripts which are
installed by default when Debian Installer is used to deploy a host. To ensure
that network configuration and name resolution are not impacted, the
:ref:`debops.resolved` role will symlink its own generated :file:`resolv.conf`
file only when the :command:`systemd-networkd` service is detected via the
Ansible local fact managed by the :ref:`debops.networkd` role.

Refer to the ``/ETC/RESOLF.CONF`` section of the
:man:`systemd-resolved.service(8)` manual page for more information on how the
service interacts with the config file.


Example inventory
-----------------

The ``debops.resolved`` role is included by default in the ``common.yml`` DebOps
playbook; you don't need to add hosts to any Ansible groups to enable it.


Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.resolved`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/resolved.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::resolved``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.
