.. Copyright (C) 2021 Maciej Delmanowski <drybjed@gmail.com>
.. Copyright (C) 2021 DebOps <https://debops.org/>
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting started
===============

.. only:: html

   .. contents::
      :local:


Overview of APT repository instances
------------------------------------

The :ref:`debops.reprepro` role sets up and manages APT repositories in one or
multiple "instances". A single GPnuG keyring is used to manage GPG keys of
uploaders and the key used to sign the repository. Public contents of the APT
repositories are published using the :ref:`debops.nginx` role. Each repository
is configured with an upload queue using WebDAV which allows package
maintainers to upload signed ``.deb`` packages using the :command:`dput`
command.

Each instance consists of the repository data files
located in :file:`/var/local/reprepro/repositories/<instance>/` directory, an
incoming queue in :file:`/var/spool/reprepro/<instance>/incoming/` directory
and public contents of the APT repository stored in
:file:`/srv/www/reprepro/sites/<instance>/public/` directory. The root paths
for these directories can be changed using default variables, if necessary.

By default APT repositories are accessible publicly. Each instance can be
configured to disable public access and require HTTP Basic Authentication to
access the repository contents; this can be utilized to provide controlled
access to the software packages.


Important configuration variables
---------------------------------

:envvar:`reprepro__gpg_uploaders_keys`
  The default configuration sets up a simple APT repository for recent Debian
  releases, including the next Testing release. To allow developers to upload
  packages to it, their GPG keys need to be added to the repository keyring. You
  can specify them using the :envvar:`reprepro__gpg_uploaders_keys` list. The
  keys are managed using the :ref:`debops.keyring` role, and can be stored either
  on a keyserver network, or in the local :file:`ansible/keyring/` directory on
  the Ansible Controller. See the role documentation for more details.

:envvar:`reprepro__origin`
  This variable is used to create the GPG key used to sign the APT
  repositories, and is added to the repository metadata in the ``Origin:``
  field which can be used by :man:`apt_preferences(5)` to control package
  policy. It's derived by default from the :ref:`debops.machine` role
  configuration, or lacking that, from the DNS domain of the host.

Reprepro maintenance, SSH access
--------------------------------

Some operations on the APT repositories require manual access to them to
execute :command:`reprepro` commands. The role configures the UNIX account to
allow SSH access by administrators. List of the SSH keys added to the account
is defined in the :envvar:`reprepro__admin_sshkeys` variable and by default
will include the SSH keys of the person executing the role.


Package uploading using :command:`dput`
---------------------------------------

You can use the :man:`dput(1)` command to upload the build ``.deb`` packages to
the repository over HTTPS. An example :file:`~/.dput.cf` configuration file:

.. code-block:: none

   [repo]
   fqdn = repo.example.org
   incoming = /upload
   method = https
   allow_unsigned_uploads = 0
   progress_indicator = 2
   allowed_distributions = .*


Example inventory
-----------------

To install and configure ``reprepro`` on a given host, it should be included in
a specific Ansible inventory group:

.. code-block:: none

   [debops_all_hosts]
   hostname

   [debops_service_reprepro]
   hostname

Example playbook
----------------

If you are using this role without DebOps, here's an example Ansible playbook
that uses the ``debops.reprepro`` role:

.. literalinclude:: ../../../../ansible/playbooks/service/reprepro.yml
   :language: yaml
   :lines: 1,5-


Ansible tags
------------

You can use Ansible ``--tags`` or ``--skip-tags`` parameters to limit what
tasks are performed during Ansible run. This can be used after a host was first
configured to speed up playbook execution, when you are sure that most of the
configuration is already in the desired state.

Available role tags:

``role::reprepro``
  Main role tag, should be used in the playbook to execute all of the role
  tasks as well as role dependencies.


Other resources
---------------

List of other useful resources related to the ``debops.reprepro`` Ansible role:

- Manual pages: :man:`reprepro(1)`, :man:`sources.list(5)`,
  :man:`apt_auth.conf(5)`, :man:`dput(1)`, :man:`dput.cf(5)`

- `Creating an APT repository with reprepro`__ on Debian Wiki

  .. __: https://wiki.debian.org/DebianRepository/SetupWithReprepro

- Example of `creation and maintenance of an APT repository mirror`__

  .. __: https://www.waveguide.se/?article=create-you-own-customized-debian-repository-mirror
