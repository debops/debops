.. Copyright (C) 2024 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2024 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:
      :depth: 2

Why...?
-------

Let's get the elephant in the room out of the way - NixOS already has support
for remote host management. The :command:`nixos-rebuild` command `can rebuild
and deploy NixOS configuration to remote hosts`__. There are also many
solutions for managing multiple NixOS hosts, like `deploy-rs`__, `colmena`__
and others. And this is just another one, tailored for integration with
environments managed by DebOps.

The :ref:`debops.nixos` role is a very simple way to manage NixOS
configuration: push a set of config files to the remote host via Ansible, run
the :command:`nixos-rebuild switch` command on the remote host and you're
finished. The strength of this solution is the ability to integrate NixOS hosts
with your existing Debian/Ubuntu environment managed by Ansible/DebOps. You can
use Jinja to generate NixOS configuration, you can leverage the multi-level
Ansible inventory to create Nix configurations split between groups and hosts,
you can lookup passwords and other data managed by the :ref:`debops.secret`
role or even generate your own passwords and store them easily using the
``lookup("password")`` Ansible lookup.

It's a great entry point into the NixOS world for Ansible and DebOps veterans. :)

N.B.: The Nix package manager is available in `Debian`__ and `Ubuntu`__
distributions as ``nix-bin`` and ``nix-setup-systemd`` packages. It can be used
to setup and manage Nix-based environments on existing Debian/Ubuntu hosts.
This role is not designed with this setup in mind.

.. __: https://nixcademy.com/posts/nixos-rebuild-remote-deployment/
.. __: https://github.com/serokell/deploy-rs
.. __: https://github.com/zhaofengli/colmena
.. __: https://tracker.debian.org/pkg/nix
.. __: https://launchpad.net/ubuntu/+source/nix


NixOS requirements
------------------

The host should have NixOS installed already before it can be configured. You
can download and use an ISO-based installed from the `official NixOS download
page`__.  An alternative way for installation is to use the iPXE boot menu
configured with the :ref:`debops.ipxe` role (in tandem with the
:ref:`debops.dnsmasq` or the :ref:`debops.tftpd` roles) to boot the NixOS
installer available via the `netboot.xyz`__ service. In the iPXE boot menu, use
"Netboot.xyz Boot Menu", "Linux Network Installs", "NixOS" and select the
preferred release. This will download and boot the basic installer, in which
you can set up and install the OS (check `NixOS Installation Guide`__ for
instructions).

To be able to use Ansible on a NixOS host, it requires an installed and enabled
OpenSSH server, installed ``python3`` package and a way to either elevate
privileges to the UNIX ``root`` account (for example via :command:`sudo`), or
to provide access to the ``root`` account over SSH. The example
:file:`configuration.nix` configuration file provided in the
:envvar:`nixos__default_configuration` variable includes configuration which
sets up the required environment.

.. __: https://nixos.org/download/
.. __: https://netboot.xyz/
.. __: https://nixos.wiki/wiki/NixOS_Installation_Guide


Different ways to configure NixOS
---------------------------------

The role provides multiple ways to configure a NixOS host. Different methods
are executed in the described order (:command:`git`-based configuration,
YAML-based configuration, custom templates). With careful planning, they can be
used together to achieve different things.

.. _nixos__ref_in_git:

:command:`git`-based configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users can clone one or more :command:`git` repositories to the
:file:`/etc/nixos/` directory or its subdirectories to provide Nix
configuration files on the host (this is the fastest method from the available
ones). The repositories are configured using the ``nixos__*_repositories``
variables, documented in the :ref:`nixos__ref_repositories` section of the
documentation.

The :file:`/etc/nixos/` directory requires special consideration if it will be
managed using a :command:`git` repository. Since :command:`git` itself does not
permit cloning a repository to a non-empty directory, the :ref:`debops.nixos`
role can automatically archive the configuration directory, remove it, clone
the specified :command:`git` repository and re-sync the original configuration
into place, by default ensuring that files committed in the repository are not
overwritten. This allows, for example, to keep the
:file:`/etc/nixos/hardware-configuration.nix` file outside of the
:command:`git` repository to ensure that per-host hardware configuration is not
overwritten.

To enable this, users should set the :envvar:`nixos__git_resync` variable on
the command line on first clone of the repository:

.. code-block:: console

   debops run nixos -e 'nixos__git_resync=true'

After the repository is cloned, the variable doesn't need to be set anymore.

YAML-based configuration in Ansible inventory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NixOS configuration files can be defined in Ansible inventory variables using
YAML dictionaries. This is done using the ``nixos__*_configuration`` variables,
which are documented in the :ref:`nixos__ref_configuration` section of the
documentation. The role uses the :ref:`universal_configuration` system to
manage YAML-based configuration entries.

This method of configuration can leverage the multiple levels of Ansible
inventory hierarchy (all hosts, multiple host groups, specific hosts) to mix
and match NixOS configuration files on multiple hosts in a cluster. Files can
be created on subdirectories of the :file:`/etc/nixos/` directory, can be
generated or removed conditionally, and use Jinja expressions to generate Nix
code with access to Ansible variables and lookup plugins.

Custom templates in :file:`ansible/views/<view>/nixos/` subdirectory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The role can use the `community.general.filetree`__ Ansible lookup plugin to
generate NixOS configuration files based on Jinja templates stored in the
:file:`ansible/views/<view>/nixos/` subdirectory of the DebOps project
directory (similar system to the one utilized by the :ref:`debops.resources`
role). This functionality is documented in the :ref:`nixos__ref_templates`
section of the documentation.

NixOS configuration stored and managed this way is easiest to edit using
a preferred text editor with Nix syntax highlighting. The directory structure
allows for multiple levels of hierarchy based on Ansible inventory hierarchy
(all hosts, multiple groups of hosts, specific hosts). One downside is
inability to control when the files are removed from remote hosts, they have to
be removed manually or via other means.

.. __: https://docs.ansible.com/ansible/latest/collections/community/general/filetree_lookup.html


Example inventory
-----------------

To configure a NixOS host using Ansible, you need to add it in the Ansible
inventory under a special group, not managed by the main DebOps playbooks:

.. code-block:: none

   [debops_nixos_hosts]
   hostname   ansible_host=hostname.example.org

Use one or more of the methods outlined above to prepare the NixOS
configuration files.


Example playbook
----------------

The :ref:`debops.nixos` role is NOT included in the main DebOps playbooks. It
has its own :file:`nixos.yml` playbook which can be run separately from the
rest of the other playbooks. To use it, run the command:

.. code-block:: console

   debops run nixos

Or, in a check mode, with a specific host:

.. code-block:: console

   debops check nixos -l hostname

To apply changes on the whole infrastructure at once, you can use the command:

.. code-block:: console

   debops run site nixos

If you are using this role without DebOps, here's an example Ansible playbook
that uses the :ref:`debops.nixos` role:

.. literalinclude:: ../../../../ansible/playbooks/nixos.yml
   :language: yaml
   :lines: 1,15-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::nixos``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.

``skip::nixos``
  Main role tag, should be used in the playbook to skip all of the role tasks.

Other resources
---------------

List of other useful resources related to the :ref:`debops.nixos` Ansible role:

- :ref:`other_projects_NixOS_module` in :ref:`other_projects`

- Official `NixOS Manual`__

  .. __: https://nixos.org/manual/nixos/stable/

- Official `NixOS Wiki`__

  .. __: https://wiki.nixos.org

- Collection of example `NixOS configurations`__ on NixOS Wiki

  .. __: https://wiki.nixos.org/wiki/Configuration_Collection

- Comparison of `Debian and NixOS management commands`__

  .. __: https://nixos.wiki/wiki/Nix_to_Debian_phrasebook

- Beginners Guide to `NixOS & Flakes`__, an unofficial book for beginners

  .. __: https://nixos-and-flakes.thiscute.world/
